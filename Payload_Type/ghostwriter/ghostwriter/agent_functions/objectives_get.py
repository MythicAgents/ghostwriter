from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ObjectivesGetArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [

        ]

    async def parse_arguments(self):
        #self.load_args_from_json_string(self.command_line)
        pass

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ObjectivesGet(CommandBase):
    cmd = "objectives_get"
    needs_admin = False
    help_cmd = "objectives_get"
    description = "Get information about the project's current objectives"
    version = 2
    author = "@its_a_feature_"
    argument_class = ObjectivesGetArguments
    supported_ui_features = ["ghostwriter:objectives_get"]
    browser_script = BrowserScript(script_name="objectives_get", author="@its_a_feature_")
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
        objectives_get_query = gql(
            """
            query objectives_get($projectId: bigint!) {
              objective(where: {projectId: {_eq: $projectId}}) {
                complete
                deadline
                description
                id
                markedComplete
                objective
                objectivePriority {
                  id
                  priority
                }
                objectiveStatus {
                  objectiveStatus
                }
                objectiveSubTasks {
                  complete
                  deadline
                  id
                  task
                  objectiveStatus {
                    objectiveStatus
                  }
                  markedComplete
                }
              }
            }
            """
        )
        try:
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData, query=objectives_get_query,
                                                                              variable_values={"projectId": GhostwriterAPI.get_project_id(taskData)})
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
