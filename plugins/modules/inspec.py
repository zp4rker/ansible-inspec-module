#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import subprocess, os
from json import JSONDecodeError

def run_module():
    backend_options = ['ssh', 'winrm']

    module_args = dict(
        src = dict(type = 'str', required = True),

        backend = dict(type = 'str', required = False, default = 'ssh'),
        host = dict(type = 'str', required = False),
        username = dict(type = 'str', required = False),
        password = dict(type = 'str', required = False, no_log = True),
    )

    result = dict(
        changed = False,
        tests = []
    )

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        if not os.path.exists(module.params['src']):
            module.fail_json(msg = f'Could not find file or directory at: {module.params["src"]}')

        if module.params['host'] is None:
            command = f'inspec exec {module.params["src"]} --reporter json-min'
        else:
            if module.params['username'] is None:
                module.fail_json(msg = 'username must be defined to run on a remote target!')
            if module.params['backend'] not in backend_options:
                module.fail_json(msg = 'Invalid backend type. Available options: ssh, winrm')
            if os.environ.get('SSH_AUTH_SOCK') is None and module.params['password'] is None:
                module.fail_json(msg = 'password must be defined to run on a remote target! Alternatively, you can use SSH_AUTH_SOCK.')

            if os.environ.get('SSH_AUTH_SOCK') is None:
                command = f'inspec exec -b {0} --host {1} --user {2} --password {3} {module.params["src"]} --reporter json-min'.format(
                    module.params['backend'], 
                    module.params['host'], 
                    module.params['username'],
                    module.params['password']
                )
            else:
                command = f'inspec exec -b {0} --host {1} --user {2} {module.params["src"]} --reporter json-min'.format(
                    module.params['backend'], 
                    module.params['host'], 
                    module.params['username']
                )


        inspec_result = subprocess.run(f'inspec exec {module.params["src"]} --reporter json-min'.split(" "), text = True, capture_output = True)

        if inspec_result.stderr is not None:
            if 'cannot execute without accepting the license' in inspec_result.stderr:
                module.fail_json(msg = 'This module requires the Inspec license to be accepted.')
            elif "Don't understand inspec profile" in inspec_result.stderr:
                module.fail_json(msg = 'Inspec was unable to read the profile structure.')
            elif 'Could not fetch inspec profile' in inspec_result.stderr:
                module.fail_json(msg = 'Inspec was unable to read that profile or test.')

        result['tests'] = module.from_json(inspec_result.stdout)['controls']

        failed = False
        for test in result['tests']:
            if test['status'] == 'failed':
                failed = True
                break

        if failed:
            module.fail_json(msg = 'Some tests failed!', **result)
        else:
            module.exit_json(msg = 'All tests passed.', **result)
    except JSONDecodeError:
        module.fail_json(msg = f'Inspec did not return correctly. The error was: {inspec_result.stderr}')
    except FileNotFoundError:
        module.fail_json(msg = 'This module requires inspec to be installed on the host machine.')
    except Exception as error:
        module.fail_json(msg = f'Encountered an error: {error}')


def main():
    run_module()


if __name__ == '__main__':
    main()