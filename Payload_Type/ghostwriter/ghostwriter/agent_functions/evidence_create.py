import datetime

from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class EvidenceCreateArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="finding_id",
                display_name="Finding ID",
                type=ParameterType.String,
                description="ID for the finding to associate this evidence with",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=True
                )]
            ),
            CommandParameter(
                name="document",
                display_name="Original Filename",
                type=ParameterType.String,
                description="Original filename of the document uploaded as evidence",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
            CommandParameter(
                name="description",
                display_name="Description",
                description="Description of the evidence",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=4,
                    required=False
                )]
            ),
            CommandParameter(
                name="caption",
                display_name="Caption",
                type=ParameterType.String,
                description="Caption for the evidence in the report",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=5,
                    required=False
                )]
            ),
            CommandParameter(
                name="friendlyName",
                display_name="Friendly Name",
                type=ParameterType.String,
                description="Friendly name for the evidence to show in the UI",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=6,
                    required=True
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class EvidenceCreate(CommandBase):
    cmd = "evidence_create"
    needs_admin = False
    help_cmd = "evidence_create -finding_id 10 -friendlyName my custom evidence"
    description = "Create a piece of evidence for a specific finding. Note: No files are uploaded yet as part of this evidence. Still need a dedicated file upload API from ghostwriter to add that piece."
    version = 1
    author = "@its_a_feature_"
    argument_class = EvidenceCreateArguments
    supported_ui_features = ["ghostwriter:evidence_create"]
    browser_script = BrowserScript(script_name="evidence_create", author="@its_a_feature_")
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
        evidence_create_blank_mutation = gql(
            """
            mutation evidenceCreate($finding_id: bigint!, $document: String, $description: String, $caption: String, $uploadDate: date!, $friendlyName: String! ) {
              insert_evidence_one(object: {findingId: $finding_id, document: $document, description: $description, caption: $caption, uploadDate: $uploadDate, friendlyName: $friendlyName}) {
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

            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=evidence_create_blank_mutation,
                                                                              variable_values={"finding_id": taskData.args.get_arg("finding_id"),
                                                                                               "description": taskData.args.get_arg("description"),
                                                                                               "document": taskData.args.get_arg("document"),
                                                                                               "caption": taskData.args.get_arg("caption"),
                                                                                               "friendlyName": taskData.args.get_arg("friendlyName"),
                                                                                               "uploadDate": str(datetime.datetime.now())})
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
