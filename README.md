# Ansible Collection - zp4rker.inspec

Executing Inspec profiles from Ansible.


## Usage

### Same machine

```yaml
- name: Run inspec tests
  inspec:
    src: /path/to/profile
```

### Remote target

```yaml
- name: Run inspec tests on remote target
  delegate_to: localhost
  inspec:
    src: /local/path/to/profile
    backend: ssh
    host: some.host.com
    username: root
    privkey: /path/to/privatekey
```

### Options

| Option           | Description                                                                    | Required                       | Default |
|------------------|--------------------------------------------------------------------------------|--------------------------------|---------|
| src              | The path to the Inspec profile or test file.                                   | True                           |         |
| backend          | The backend transport to use for remote targets. Available options: ssh, winrm | False                          | ssh     |
| host             | The host to use for remote targets.                                            | If running on a remote target. |         |
| username         | The username to use for remote targets.                                        | If running on a remote target. |         |
| password         | The password to use for remote targets.                                        | If running on a remote target. |         |
| privkey          | The path to the private key to use for remote targets. (SSH)                   | If running on a remote target. |         |
| binary_path      | The optional path to inspec or cinc-auditor binary                             | False                          |         |
| show_only_failed | Show only failed tests                                                         | False                          |         |


## Return

### Successful

```
ok: [testhost] => {"changed": false, "msg": "All tests passed.", "tests": [{"code_desc": "File /tmp/some_file.txt is expected to exist", "id": "(generated from test_1.rb:1 41bb5413a1b4562f8e824b8d438bb29c)", "profile_id": "tests from .tmp.test_1.rb", "profile_sha256": "2be1077607725f78d62eb11247b1145547f497b638ecb9e0811d6ee4fd0006fb", "status": "passed"}]}
```

### Failed
```
fatal: [testhost]: FAILED! => {"changed": false, "msg": "Some tests failed!", "tests": [{"code_desc": "File /tmp/some_file.txt is expected to exist", "id": "(generated from test_1.rb:1 ae673db9d0ef3a4313737d804bb875c3)", "profile_id": "test-profile", "profile_sha256": "b1bd53530a57b0c167489366f842aba22c9f44ad855ef385e78885bcbfa2c6de", "status": "passed"}, {"code_desc": "File /tmp/another_file.txt is expected to exist", "id": "(generated from test_2.rb:1 6f503929413724ed431052d515dfeb4e)", "message": "expected File /tmp/another_file.txt to exist", "profile_id": "test-profile", "profile_sha256": "b1bd53530a57b0c167489366f842aba22c9f44ad855ef385e78885bcbfa2c6de", "status": "failed"}]}
```
