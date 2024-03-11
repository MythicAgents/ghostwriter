from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class FindingsCreateBlankArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
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
                name="report",
                display_name="Report Title",
                type=ParameterType.String,
                description="Name of the report (or closest approximation) if multiple reports exist for this project",
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=3,
                    required=True
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
                name="findingType",
                display_name="Type of Finding",
                type=ParameterType.ChooseOne,
                description="Type of finding",
                dynamic_query_function=self.get_findings,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=5,
                    required=True
                )]
            ),
            CommandParameter(
                name="severityType",
                display_name="Severity Rating",
                type=ParameterType.ChooseOne,
                description="Severity Rating",
                dynamic_query_function=self.get_severity,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=6,
                    required=True
                )]
            ),
        ]

    async def get_findings(self, callback: PTRPCDynamicQueryFunctionMessage) -> PTRPCDynamicQueryFunctionMessageResponse:
        response = PTRPCDynamicQueryFunctionMessageResponse(Success=False)
        payload_resp = await SendMythicRPCPayloadSearch(MythicRPCPayloadSearchMessage(
            PayloadUUID=callback.PayloadUUID
        ))
        if payload_resp.Success:
            if len(payload_resp.Payloads) == 0:
                await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                    CallbackId=callback.Callback,
                    Message=f"Failed to get payload: {payload_resp.Error}",
                    MessageLevel="warning"
                ))
                response.Error = f"Failed to get payload: {payload_resp.Error}"
                return response
            payload = payload_resp.Payloads[0]
            fakeTaskData = PTTaskMessageAllData()
            fakeTaskData.BuildParameters = payload.BuildParameters
            fakeTaskData.Secrets = callback.Secrets
            choices = await GhostwriterAPI.get_finding_types(taskData=fakeTaskData)
            response.Choices = [x["findingType"] for x in choices]
            response.Success = True
            return response
        else:
            await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                CallbackId=callback.Callback,
                Message=f"Failed to get payload: {payload_resp.Error}",
                MessageLevel="warning"
            ))
            response.Error = f"Failed to get payload: {payload_resp.Error}"
            return response

    async def get_severity(self, callback: PTRPCDynamicQueryFunctionMessage) -> PTRPCDynamicQueryFunctionMessageResponse:
        response = PTRPCDynamicQueryFunctionMessageResponse(Success=False)
        payload_resp = await SendMythicRPCPayloadSearch(MythicRPCPayloadSearchMessage(
            PayloadUUID=callback.PayloadUUID
        ))
        if payload_resp.Success:
            if len(payload_resp.Payloads) == 0:
                await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                    CallbackId=callback.Callback,
                    Message=f"Failed to get payload: {payload_resp.Error}",
                    MessageLevel="warning"
                ))
                response.Error = f"Failed to get payload: {payload_resp.Error}"
                return response
            payload = payload_resp.Payloads[0]
            fakeTaskData = PTTaskMessageAllData()
            fakeTaskData.BuildParameters = payload.BuildParameters
            fakeTaskData.Secrets = callback.Secrets
            choices = await GhostwriterAPI.get_severities(taskData=fakeTaskData)
            response.Choices = [x["severity"] for x in choices]
            response.Success = True
            return response
        else:
            await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                CallbackId=callback.Callback,
                Message=f"Failed to get payload: {payload_resp.Error}",
                MessageLevel="warning"
            ))
            response.Error = f"Failed to get payload: {payload_resp.Error}"
            return response

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class FindingsCreateBlank(CommandBase):
    cmd = "findings_create_blank"
    needs_admin = False
    help_cmd = "findings_create_blank"
    description = "Create a new blank finding for the report"
    version = 1
    author = "@its_a_feature_"
    argument_class = FindingsCreateBlankArguments
    supported_ui_features = ["ghostwriter:findings_create_blank"]
    browser_script = BrowserScript(script_name="findings_create_blank", author="@its_a_feature_")
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
        findings_create_blank_mutation = gql(
            """
            mutation findingsCreateBlank($title: String, $description: String, $reportId: bigint!, $findingTypeId: bigint!, $severityId: bigint!, $cvssScore: float8) {
              insert_reportedFinding_one(object: {reportId: $reportId, description: $description, title: $title, findingTypeId: $findingTypeId, severityId: $severityId, cvssScore: $cvssScore, extraFields: {}}) {
                id
                complete
                cvssScore
                description
                assignedTo {
                  username
                }
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
            severityId = None
            findingTypeId = None
            severities = await GhostwriterAPI.get_severities(taskData=taskData)
            findingTypes = await GhostwriterAPI.get_finding_types(taskData=taskData)
            for s in severities:
                if s["severity"] == taskData.args.get_arg("severityType"):
                    severityId = s["id"]
            for ft in findingTypes:
                if ft["findingType"] == taskData.args.get_arg("findingType"):
                    findingTypeId = ft["id"]
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=findings_create_blank_mutation,
                                                                              variable_values={"title": taskData.args.get_arg("title"),
                                                                                               "description": taskData.args.get_arg("description"),
                                                                                               "reportId": reports[0]["id"],
                                                                                               "cvssScore": taskData.args.get_arg("cvssScore"),
                                                                                               "severityId": severityId,
                                                                                               "findingTypeId": findingTypeId})
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
