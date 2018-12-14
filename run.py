import sys
import os
#
# if 'LAMBDA_TASK_ROOT' in os.environ:
#     sys.path.insert(0, f"{os.environ['LAMBDA_TASK_ROOT']}/libs")
#
# sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


from h import core


if __name__ == '__main__':
    core.run()
