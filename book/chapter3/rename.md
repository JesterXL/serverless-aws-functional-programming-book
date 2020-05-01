# Rename Hello World

If you want to rename a resource, here's the short version:
- Rename your "hello_world" folder to "download_benner".
- Rename your unit test to reference it: `from download_benner import app`
- Change the `CodeUri` in your `template.yaml` to reference the new folder: `CodeUri: hello_world/`

To change the name, do a quick `sam build && sam deploy`. Notice it didn't actually deploy anything because, at least remotely, nothing changed. If you had changed the contents of your code, it would. Let's do that!