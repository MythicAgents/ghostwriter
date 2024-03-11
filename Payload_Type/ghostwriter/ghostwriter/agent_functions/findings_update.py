from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class FindingsUpdateArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="finding_id",
                display_name="Finding ID",
                type=ParameterType.Number,
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=0,
                    required=False
                )]
            ),
            CommandParameter(
                name="title",
                display_name="Finding Title",
                type=ParameterType.String,
                description="Title for the new finding",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=False
                )]
            ),
            CommandParameter(
                name="description",
                display_name="Finding Description",
                type=ParameterType.String,
                description="Description for the new finding",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
            CommandParameter(
                name="cvssScore",
                display_name="CVSS Score",
                type=ParameterType.String,
                default_value="5.0",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=4,
                    required=True
                )]
            ),
            CommandParameter(
                name="complete",
                display_name="Complete",
                type=ParameterType.Boolean,
                description="Finding is complete and finished review",
                default_value=False,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=7,
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class FindingsUpdate(CommandBase):
    cmd = "findings_update"
    needs_admin = False
    help_cmd = "findings_update"
    description = "Update an existing finding attached to a report"
    version = 1
    author = "@its_a_feature_"
    argument_class = FindingsUpdateArguments
    supported_ui_features = ["ghostwriter:findings_update"]
    browser_script = BrowserScript(script_name="findings_update", author="@its_a_feature_")
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
        findings_update_mutation = gql(
            """
            mutation findingsUpdate($finding_id: bigint!, $title: String, $description: String, $cvssScore: float8, $complete: Boolean!) {
              update_reportedFinding_by_pk(pk_columns: {id: $finding_id}, _set: {title: $title, description: $description, cvssScore: $cvssScore, complete: $complete }){
                id
              }
            }
            """
        )
        try:
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=findings_update_mutation,
                                                                              variable_values={"title": taskData.args.get_arg("title"),
                                                                                               "description": taskData.args.get_arg("description"),
                                                                                               "cvssScore": taskData.args.get_arg("cvssScore"),
                                                                                               "finding_id": taskData.args.get_arg("finding_id"),
                                                                                               "complete": taskData.args.get_arg("complete")})
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
