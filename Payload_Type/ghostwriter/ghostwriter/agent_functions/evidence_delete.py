from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class EvidenceDeleteArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="evidence_id",
                display_name="Evidence ID",
                type=ParameterType.Number,
                description="The ID of the evidence to delete",
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=True
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class EvidenceDelete(CommandBase):
    cmd = "evidence_delete"
    needs_admin = False
    help_cmd = "evidence_delete -evidence_id 10"
    description = "Delete a specific piece of evidence from Ghostwriter"
    version = 2
    author = "@its_a_feature_"
    argument_class = EvidenceDeleteArguments
    supported_ui_features = ["ghostwriter:evidence_delete"]
    browser_script = BrowserScript(script_name="evidence_delete", author="@its_a_feature_")
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
        evidence_delete_query = gql(
            """
            mutation deleteEvidence($evidence_id: bigint!) {
              delete_evidence_by_pk(id: $evidence_id) {
                caption
                description
                document
                findingId
                friendlyName
                id
                uploadDate
                uploadedById
                user {
                  username
                }
                report {
                    title
                }
                finding {
                  title
                  report {
                    title
                  }
                }
              }
            }
            """
        )
        try:

            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=evidence_delete_query,
                                                                              variable_values={"evidence_id": taskData.args.get_arg("evidence_id")})
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
