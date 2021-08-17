#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import subprocess, os.path
from json import JSONDecodeError

def run_module():
    module_args = dict(
        src=dict(type = 'str', required = True)
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