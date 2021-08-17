#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: test

short_description: This is my test module

version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    src:
        description: The path of the file to read.
        required: true
        type: str

author:
    - Zaeem Parker (@zp4rker)
'''

EXAMPLES = r'''
- name: Read lines from /tmp/test.txt
  zp4rker.inspec.test:
    src: /tmp/test.txt
'''

RETURN = r'''
lines:
    description: The lines read from the file
    type: list
    returned: always
    sample:
        - line 1
        - line 2
        - line 3
'''

from ansible.module_utils.basic import AnsibleModule


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

    f = open(module.params['src'], 'r')
    result['lines'] = f.read().split('\n')

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()