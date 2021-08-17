#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
import os, json
from json import JSONDecodeError

def run_module():
    module_args = dict(
        src=dict(type = 'str', required = True)
    )

    result = dict(
        changed = False,
        lines = []
    )

    module = AnsibleModule(
        argument_spec = module_args,
        supports_check_mode = True
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        inspec_result = os.popen(f'inspec exec {module.params["src"]} --reporter json-min').read()
        result['inspec'] = json.loads(inspec_result)

        module.exit_json(**result)
    except JSONDecodeError:
        module.fail_json(msg = f'Inspec did not run correctly. The error was: {inspec_result}')
    except Exception as error:
        module.fail_json(msg = f'Encountered an error: {error}')


def main():
    run_module()


if __name__ == '__main__':
    main()