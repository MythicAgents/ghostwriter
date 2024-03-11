from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class FindingsDeleteArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="finding_id",
                default_value=0,
                description="ID of the finding to delete",
                type=ParameterType.Number
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class FindingsDelete(CommandBase):
    cmd = "findings_delete"
    needs_admin = False
    help_cmd = "findings_delete -finding_id 10"
    description = "Delete a finding on a report"
    version = 1
    author = "@its_a_feature_"
    argument_class = FindingsDeleteArguments
    supported_ui_features = ["ghostwriter:findings_delete"]
    browser_script = BrowserScript(script_name="findings_delete", author="@its_a_feature_")
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
        try:
            delete_finding = gql(
                """
                mutation deleteFinding($finding_id: bigint!){
                    delete_reportedFinding_by_pk(id: $finding_id){
                        id
                    }
                }
                """
            )
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData=taskData, query=delete_finding,
                                                                              variable_values={
                                                                                  "finding_id": taskData.args.get_arg("finding_id"),
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
