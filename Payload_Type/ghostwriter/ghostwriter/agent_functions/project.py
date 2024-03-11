from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ProjectArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class Project(CommandBase):
    cmd = "project"
    needs_admin = False
    help_cmd = "project"
    description = "Get information about the current project"
    version = 1
    author = "@its_a_feature_"
    argument_class = ProjectArguments
    supported_ui_features = ["ghostwriter:project"]
    browser_script = BrowserScript(script_name="project", author="@its_a_feature_")
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
            reports_query = gql(
                """
                query getProject($projectId: bigint!){
                    project_by_pk(id: $projectId){
                        client {
                          name
                          codename
                          shortName
                        }
                        assignments {
                          user {
                            username
                          }
                        }
                        deconflictions {
                          alertSource
                          alertTimestamp
                          deconflictionStatus {
                            status
                          }
                          description
                          title
                        }
                    }
                }
                """
            )
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData=taskData, query=reports_query,
                                                                              variable_values={
                                                                                  "projectId": GhostwriterAPI.get_project_id(
                                                                                      taskData=taskData),
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
