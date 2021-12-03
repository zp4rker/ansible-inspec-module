#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import os
from json import JSONDecodeError

def run_module():
    module_args = dict(
        src = dict(type = 'str', required = True),

        backend = dict(type = 'str', required = False, default = 'ssh', choices = ['ssh', 'winrm']),
        host = dict(type = 'str', required = False),
        username = dict(type = 'str', required = False),
        password = dict(type = 'str', required = False, no_log = True),
        privkey = dict(type = 'str', required = False),
        binary_path = dict(type = 'str', required = False),
        controls = dict(type = 'list', required = False)
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

    bin_path = module.params.get('binary_path')

    if bin_path is not None:
        run_command = bin_path
    else:
        run_command = module.get_bin_path('inspec', required=True)

    controls = module.params.get('controls')

    # if no controls are defined, use a regex to match all controls
    if not controls:
        controls = "/.*/"
    else:
        controls = " ".join(map(str,controls))

    try:
        if not os.path.exists(module.params['src']):
            module.fail_json(msg = f'Could not find file or directory at: {module.params["src"]}')

        if not module.params['host']:
            command = f'{run_command} exec {module.params["src"]} --controls {controls} --reporter json-min'
        else:
            if not module.params['username']:
                module.fail_json(msg = 'username must be defined to run on a remote target!')
            if not os.environ.get('SSH_AUTH_SOCK') and not module.params['password'] and not module.params['privkey']:
                module.fail_json(msg = 'password or privkey must be defined to run on a remote target! Alternatively, you can use SSH_AUTH_SOCK.')

            if os.environ.get('SSH_AUTH_SOCK'):
                command = '{} exec {} -b {} --host {} --user {} --controls {} --reporter json-min'.format(
                    run_command,
                    module.params['src'],
                    module.params['backend'],
                    module.params['host'],
                    module.params['username'],
                    controls
                )
            elif module.params['privkey']:
                command = '{} exec {} -b {} --host {} --user {} -i {} --controls {} --reporter json-min'.format(
                    run_command,
                    module.params['src'],
                    module.params['backend'],
                    module.params['host'],
                    module.params['username'],
                    module.params['privkey'],
                    controls
                )
            else:
                command = '{} exec {} -b {} --host {} --user {} --password {} --controls {} --reporter json-min'.format(
                    run_command,
                    module.params['src'],
                    module.params['backend'],
                    module.params['host'],
                    module.params['username'],
                    module.params['password'],
                    controls
                )

        rc, stdout, stderr = module.run_command(command)
        # inspec_result = subprocess.run(command.split(" "), text = True, capture_output = True)

        # if inspec_result.stderr:
        if stderr:
            # if 'cannot execute without accepting the license' in inspec_result.stderr:
            if 'cannot execute without accepting the license' in stderr:
                module.fail_json(msg = 'This module requires the Inspec license to be accepted.')
            # elif "Don't understand inspec profile" in inspec_result.stderr:
            elif "Don't understand inspec profile" in stderr:
                module.fail_json(msg = 'Inspec was unable to read the profile structure.')
            # elif 'Could not fetch inspec profile' in inspec_result.stderr:
        elif 'Could not fetch inspec profile' in stderr:
                module.fail_json(msg = 'Inspec was unable to read that profile or test.')

        # result['tests'] = module.from_json(inspec_result.stdout)['controls']
        result['tests'] = module.from_json(stdout)['controls']

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
        # module.fail_json(msg = f'Inspec did not return correctly. The error was: {inspec_result.stderr}')
        module.fail_json(msg = f'Inspec did not return correctly. The error was: {stderr}')
    except FileNotFoundError:
        module.fail_json(msg = f'This module requires inspec to be installed on the host machine. Searched here: {run_command}')
    except Exception as error:
        module.fail_json(msg = f'Encountered an error: {error}', cmd = command)


def main():
    run_module()


if __name__ == '__main__':
    main()
