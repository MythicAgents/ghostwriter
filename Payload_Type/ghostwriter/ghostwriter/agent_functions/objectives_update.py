from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from ghostwriter.GhostwriterRequests import GhostwriterAPI
from gql import gql


class ObjectivesUpdateArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="id",
                display_name="Objective ID",
                cli_name="id",
                description="The ID of the objective to update",
                type=ParameterType.Number,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=1,
                    required=True
                )]
            ),
            CommandParameter(
                name="complete",
                display_name="Completed?",
                cli_name="complete",
                description="Update the completed status of the objective",
                default_value=False,
                type=ParameterType.Boolean,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=2,
                    required=False
                )]
            ),
            CommandParameter(
                name="description",
                display_name="Description",
                cli_name="description",
                description="The description of the objective",
                default_value="",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=3,
                    required=False
                )]
            ),
            CommandParameter(
                name="objective",
                display_name="Objective",
                cli_name="objective",
                description="The Objective's short name",
                default_value="",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=4,
                    required=False
                )]
            ),
            CommandParameter(
                name="priority",
                display_name="Priority",
                cli_name="priority",
                description="The priority of the objective",
                type=ParameterType.ChooseOne,
                choices=["Primary", "Secondary", "Tertiary"],
                default_value="Primary",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=5,
                    required=False
                )]
            ),
            CommandParameter(
                name="status",
                display_name="Status",
                cli_name="status",
                description="The current status of the objective",
                type=ParameterType.ChooseOne,
                choices=["Active", "On Hold", "In Progress", "Missed"],
                default_value="Active",
                parameter_group_info=[ParameterGroupInfo(
                    ui_position=6,
                    required=False
                )]
            )
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ObjectivesUpdate(CommandBase):
    cmd = "objectives_update"
    needs_admin = False
    help_cmd = "objectives_update"
    description = "Updates an objective"
    version = 1
    author = "@its_a_feature_"
    argument_class = ObjectivesUpdateArguments
    supported_ui_features = ["ghostwriter:objectives_update"]
    browser_script = BrowserScript(script_name="objectives_update", author="@its_a_feature_")
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
        objectives_priority_and_status_id = gql(
            """
            query priority_and_status_ids {
                objectiveStatus {
                    id
                    objectiveStatus
                }
                  objectivePriority {
                    id
                    priority
                }
            }
            """
        )
        objectives_update_mutation = gql(
            """
            mutation updateObjective($id: bigint!, $complete: Boolean, $description: String, $objective: String, $priorityId: bigint, $statusId: bigint){
                update_objective_by_pk(pk_columns: {id: $id}, _set: {complete: $complete, description:$description, objective: $objective, priorityId: $priorityId, statusId: $statusId}) {
                    complete
                    deadline
                    description
                    id
                    markedComplete
                    objective
                    objectiveStatus {
                      objectiveStatus
                    }
                    objectivePriority {
                      priority
                    }
                }
            }
            """
        )
        try:
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData,
                                                                              query=objectives_priority_and_status_id,
                                                                              variable_values={})
            if response_code != 200:
                return await GhostwriterAPI.process_standard_response(response_code=response_code,
                                                                      response_data=response_data,
                                                                      taskData=taskData,
                                                                      response=response)
            selected_priority_id = None
            selected_status_id = None
            for status in response_data["objectiveStatus"]:
                if status["objectiveStatus"] == taskData.args.get_arg("status"):
                    selected_status_id = status["id"]
            for priority in response_data["objectivePriority"]:
                if priority["priority"] == taskData.args.get_arg("priority"):
                    selected_priority_id = priority["id"]
            description = taskData.args.get_arg("description")
            if description == "":
                description = None
            objective = taskData.args.get_arg("objective")
            if objective == "":
                objective = None
            response_code, response_data = await GhostwriterAPI.query_graphql(taskData,
                                                                              query=objectives_update_mutation,
                                                                              variable_values={
                                                                                  "id": taskData.args.get_arg("id"),
                                                                                  "complete": taskData.args.get_arg("complete"),
                                                                                  "description": description,
                                                                                  "objective": objective,
                                                                                  "priorityId": selected_priority_id,
                                                                                  "statusId": selected_status_id
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
