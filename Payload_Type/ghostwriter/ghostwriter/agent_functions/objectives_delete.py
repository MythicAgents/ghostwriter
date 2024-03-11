from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ObjectivesDeleteArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="id",
                display_name="Objective ID",
                cli_name="id",
                description="The ID of the objective to delete",
                type=ParameterType.Number
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ObjectivesDelete(CommandBase):
    cmd = "objectives_delete"
    needs_admin = False
    help_cmd = "objectives_delete"
    description = "Delete an objective"
    version = 1
    author = "@its_a_feature_"
    argument_class = ObjectivesDeleteArguments
    supported_ui_features = ["ghostwriter:objectives_delete"]
    #browser_script = BrowserScript(script_name="objectives_get", author="@its_a_feature_")
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
        objectives_delete_mutation = gql(
            """
            mutation objectives_delete($id: bigint!) {
              delete_objective_by_pk(id: $id) {
                complete
                deadline
                markedComplete
                objectiveStatus {
                  objectiveStatus
                }
                objective
                description
                objectivePriority {
                    priority
                }
              }
            }
            """
        )
        try:
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=objectives_delete_mutation,
                                                                              variable_values={"id": taskData.args.get_arg("id")})
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
