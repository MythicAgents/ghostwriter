from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ObjectivesCreateSubtaskArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="objective",
                display_name="Objective",
                cli_name="objective",
                description="The Objective's short name",
                default_value="",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
            CommandParameter(
                name="complete",
                display_name="Completed?",
                cli_name="complete",
                description="Update the completed status of the objective",
                default_value=False,
                type=ParameterType.Boolean,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=4,
                    required=False
                )]
            ),
            CommandParameter(
                name="parentId",
                display_name="Parent Objective ID",
                cli_name="parentId",
                description="The ID of the parent objetive",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=True
                )]
            ),
            CommandParameter(
                name="status",
                display_name="Status",
                cli_name="status",
                description="The current status of the objective",
                type=ParameterType.ChooseOne,
                choices=["Active", "On Hold", "In Progress", "Missed"],
                default_value="Active",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=6,
                    required=False
                )]
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ObjectivesCreateSubtask(CommandBase):
    cmd = "objectives_create_subtask"
    needs_admin = False
    help_cmd = "objectives_create_subtask -objective \"Get DA\" -parentId 12"
    description = "Creates a subtask of an objective"
    version = 1
    author = "@its_a_feature_"
    argument_class = ObjectivesCreateSubtaskArguments
    supported_ui_features = ["ghostwriter:objectives_create_subtask"]
    browser_script = BrowserScript(script_name="objectives_create_subtask", author="@its_a_feature_")
    attackmapping = []
    completion_functions = {
    }

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f""
        )
        objectives_priority_and_status_id = gql(
            """
            query priority_and_status_ids {
                objectiveStatus {
                    id
                    objectiveStatus
                }
                  objectivePriority {
                    id
                    priority
                }
            }
            """
        )
        objectives_create_mutation = gql(
            """
            mutation createObjective($parentId: bigint!, $complete: Boolean, $objective: String, $statusId: bigint, $deadline: date){
                insert_objectiveSubTask_one(object: {parentId: $parentId, complete: $complete, task: $objective, statusId: $statusId, deadline: $deadline}) {
                    complete
                    deadline
                    id
                    markedComplete
                    task
                    objectiveStatus {
                      objectiveStatus
                    }
                }
            }
            """
        )
        try:
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData,
                                                                              query=objectives_priority_and_status_id,
                                                                              variable_values={})
            if response_code != 200:
                return await GhostwriterAPI.process_standard_response(response_code=response_code,
                                                                      response_data=response_data,
                                                                      taskData=taskData,
                                                                      response=response)
            selected_status_id = None
            for status in response_data["objectiveStatus"]:
                if status["objectiveStatus"] == taskData.args.get_arg("status"):
                    selected_status_id = status["id"]
            objective = taskData.args.get_arg("objective")
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData,
                                                                              query=objectives_create_mutation,
                                                                              variable_values={
                                                                                  "complete": taskData.args.get_arg("complete"),
                                                                                  "objective": objective,
                                                                                  "parentId": taskData.args.get_arg("parentId"),
                                                                                  "statusId": selected_status_id,
                                                                                  "deadline": (await GhostwriterAPI.get_project(taskData))["endDate"]
                                                                              })
            return await GhostwriterAPI.process_standard_response(response_code=response_code,
                                                                  response_data=response_data,
                                                                  taskData=taskData,
                                                                  response=response)

        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{e}".encode("UTF8"),
            ))
            response.TaskStatus = "Error: Ghostwriter Access Error"
            response.Success = False
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
