import datetime

from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class EvidenceUpdateArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="evidence_id",
                display_name="Evidence ID",
                type=ParameterType.Number,
                description="ID of the evidence entry to update",
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=True
                )]
            ),
            CommandParameter(
                name="description",
                display_name="Description",
                description="Description of the evidence",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
            CommandParameter(
                name="caption",
                display_name="Caption",
                type=ParameterType.String,
                description="Caption for the evidence in the report",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=3,
                    required=False
                )]
            ),
            CommandParameter(
                name="friendlyName",
                display_name="Friendly Name",
                type=ParameterType.String,
                description="Friendly name for the evidence to show in the UI",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=4,
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class EvidenceUpdate(CommandBase):
    cmd = "evidence_update"
    needs_admin = False
    help_cmd = "evidence_update -evidence-id 10 -friendlyName my custom evidence"
    description = "Update information about a piece of evidence"
    version = 1
    author = "@its_a_feature_"
    argument_class = EvidenceUpdateArguments
    supported_ui_features = ["ghostwriter:evidence_update"]
    browser_script = BrowserScript(script_name="evidence_update", author="@its_a_feature_")
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
        evidence_update_mutation = gql(
            """
            mutation evidenceUpdate($evidence_id: bigint!, $description: String, $caption: String, $friendlyName: String!) {
              update_evidence_by_pk(pk_columns: {id: $evidence_id}, _set: {friendlyName: $friendlyName, description: $description, caption: $caption}) {
                uploadedById
                uploadDate
                report_id
                id
                friendlyName
                findingId
                document
                description
                caption
              }
            }
            """
        )
        try:

            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=evidence_update_mutation,
                                                                              variable_values={"evidence_id": taskData.args.get_arg("evidence_id"),
                                                                                               "description": taskData.args.get_arg("description"),
                                                                                               "caption": taskData.args.get_arg("caption"),
                                                                                               "friendlyName": taskData.args.get_arg("friendlyName")})
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
