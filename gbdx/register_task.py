import gbdxtools
import json
import os

gbdx = gbdxtools.Interface()

# register the task on gbdx
json_file = 'register_task.json'
# confirm it exists
if os.path.exists(json_file):
    gbdx.task_registry.register(json_filename=json_file)
else:
    raise Exception("File does not exist: {}".format(json_file))

# extract the task name from the json
with open(json_file, 'r') as f:
    d = json.load(f)
    task_name = ':'.join([str(d['name']), str(d['version'])])

# confirm it got added
print('waiting on task registration within gbdx')
while task_name not in gbdx.task_registry.list():
    print('.')

print('task successfully registered')

# to remove the task from gbdx
# gbdx.task_registry.delete(task_name)