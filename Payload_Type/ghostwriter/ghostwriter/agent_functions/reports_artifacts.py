from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ReportsArtifactsArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [

        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ReportsArtifacts(CommandBase):
    cmd = "reports_artifacts"
    needs_admin = False
    help_cmd = "reports_artifacts"
    description = "Generate a list of the full path, filename, hash, computer, and timestamp of all files that touched disk remotely"
    version = 2
    author = "@its_a_feature_"
    argument_class = ReportsArtifactsArguments
    supported_ui_features = ["ghostwriter:reports_artifacts"]
    #browser_script = BrowserScript(script_name="findings_attach", author="@its_a_feature_")
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
        files_search = await SendMythicRPCFileSearch(MythicRPCFileSearchMessage(
            TaskID=taskData.Task.ID,
            LimitByCallback=False,
            IsScreenshot=False,
            IsDownloadFromAgent=False,
        ))
        if not files_search.Success:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=files_search.Error.encode()
            ))
            return response
        file_data = []
        for f in files_search.Files:
            # only get files that actually touched disk
            if f.FullRemotePath != "":
                file_data.append({
                    "md5": f.Md5,
                    "absolute_path": f.FullRemotePath,
                    "hostname": f.Host,
                    "timestamp": f.Timestamp
                })
        file_csv = "\n".join([f"{x['md5']},{x['absolute_path']},{x['hostname']},{x['timestamp']}" for x in file_data])
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=file_csv.encode()
        ))
        response.Success = True
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
