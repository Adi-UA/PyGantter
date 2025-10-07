from enum import Enum


class TaskField(str, Enum):
    TASK = "Task"
    START = "Start"
    END = "End"
    EFFORT = "Effort"
    RESOURCE = "Resource"
    DEPENDENCIES = "Dependencies"
    GROUP = "Group"
