from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class FindingsAttachArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="findingId",
                display_name="Finding ID",
                type=ParameterType.String,
                description="Finding Identifier",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=True
                )]
            ),
            CommandParameter(
                name="report",
                display_name="Report Title",
                type=ParameterType.String,
                description="Name of the report (or closest approximation)",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class FindingsAttach(CommandBase):
    cmd = "findings_attach"
    needs_admin = False
    help_cmd = "findings_attach -findingID 23"
    description = "Attach an existing finding to a report"
    version = 2
    author = "@its_a_feature_"
    argument_class = FindingsAttachArguments
    supported_ui_features = ["ghostwriter:findings_attach"]
    browser_script = BrowserScript(script_name="findings_attach", author="@its_a_feature_")
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
        findings_attach_mutation = gql(
            """
            mutation findingsAttach($findingId: Int!, $reportId: Int!) {
              attachFinding(findingId: $findingId, reportId: $reportId) {
                id
              }
            }
            """
        )
        try:
            report = "%" + taskData.args.get_arg("report") + "%"
            if report == "%%":
                report = "%_%"
            reports = await GhostwriterAPI.get_project_reports(taskData=taskData, title=report)
            if len(reports) == 0:
                response.Success = False
                await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                    TaskID=taskData.Task.ID,
                    Response=f"Failed to find any matching reports by that name".encode()
                ))
                return response
            if len(reports) > 1:
                response.Success = False
                await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                    TaskID=taskData.Task.ID,
                    Response=f"Report name is ambiguous, too many matching reports".encode()
                ))
                return response

            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=findings_attach_mutation,
                                                                              variable_values={"findingId": taskData.args.get_arg("findingId"),
                                                                                               "reportId": reports[0]["id"]})
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
