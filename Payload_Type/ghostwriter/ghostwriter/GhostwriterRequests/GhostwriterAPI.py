from mythic_container.MythicCommandBase import *
from ghostwriter.GhostwriterRequests.GhostwriterAPIClasses import *
from mythic_container.MythicRPC import *
from gql import gql

GHOSTWRITER_API_KEY = "GHOSTWRITER_API_KEY"


def get_project_id(taskData: PTTaskMessageAllData) -> str:
    for buildParam in taskData.BuildParameters:
        if buildParam.Name == "ProjectId":
            return buildParam.Value
    return ""


async def get_project(taskData: PTTaskMessageAllData):
    project_query = gql(
        """
        query getProject($projectId: bigint!){
            project(where: {id: {_eq: $projectId}}) {
                endDate
            }
        }
        """
    )
    result_code, result_data = await query_graphql(taskData=taskData, query=project_query,
                                                   variable_values={
                                                       "projectId": get_project_id(taskData=taskData),
                                                   })
    if result_data is not None and result_code == 200:
        if len(result_data["project"]) == 0:
            logger.error(result_data)
            return {}
        return result_data["project"][0]
    else:
        logger.error(result_data)
    return {}


async def get_severities(taskData: PTTaskMessageAllData):
    severity_query = gql(
        """
        query getSeverity{
            findingSeverity {
                id
                severity
              }
        }
        """
    )
    result_code, result_data = await query_graphql(taskData=taskData, query=severity_query)
    if result_data is not None and result_code == 200:
        return result_data["findingSeverity"]
    else:
        logger.error(result_data)
    return []


async def get_finding_types(taskData: PTTaskMessageAllData):
    finding_types_query = gql(
        """
        query getFindingTypes{
            findingType {
                id
                findingType
            }
        }
        """
    )
    result_code, result_data = await query_graphql(taskData=taskData, query=finding_types_query)
    if result_data is not None and result_code == 200:
        return result_data["findingType"]
    else:
        logger.error(result_data)
    return []


async def get_project_reports(taskData: PTTaskMessageAllData, title: str):
    reports_query = gql(
        """
        query getReports($title: String!, $projectId: bigint!){
            report(where: {projectId: {_eq: $projectId}, complete: {_eq: false}, archived: {_eq: false}, title: {_ilike: $title}}) {
                id
                title
            }
        }
        """
    )
    search_title = "%" + title + "%"
    if search_title == "%%":
        search_title = "%_%"
    result_code, result_data = await query_graphql(taskData=taskData, query=reports_query,
                                                   variable_values={
                                                       "projectId": get_project_id(taskData=taskData),
                                                       "title": search_title
                                                   })
    if result_data is not None and result_code == 200:
        return result_data["report"]
    else:
        logger.error(result_data)
    return []


def check_valid_values(api_token, url) -> bool:
    if api_token == "" or api_token is None:
        logger.error("missing apitoken")
        return False
    if url == "" or url is None:
        logger.error("missing url")
        return False
    return True


async def query_graphql(taskData: PTTaskMessageAllData, query: gql, uri: str = '/v1/graphql',
                        variable_values: dict = None) -> (int, dict):
    api_token = None
    url = None
    for buildParam in taskData.BuildParameters:
        if buildParam.Name == "URL":
            url = buildParam.Value
    if GHOSTWRITER_API_KEY in taskData.Secrets:
        api_token = taskData.Secrets[GHOSTWRITER_API_KEY]
    if not check_valid_values(api_token, url):
        return 500, "Missing GHOSTWRITER_API_KEY in User settings or missing Ghostwriter URL"
    try:
        credentials = Credentials(api_token=api_token)
        client = GhostwriterClient(url=url.rstrip("/") + uri, credentials=credentials)
        response = await client.graphql_query(query=query, variable_values=variable_values)
        logger.info(f"Ghostwriter Query: {uri}")
        if response is not None:
            return 200, response
        else:
            return 500, client.last_error
    except Exception as e:
        logger.exception(f"[-] Failed to query Ghostwriter: \n{e}\n")
        raise Exception(f"[-] Failed to query Ghostwriter: \n{e}\n")


async def process_standard_response(response_code: int, response_data: any,
                                    taskData: PTTaskMessageAllData, response: PTTaskCreateTaskingMessageResponse) -> \
        PTTaskCreateTaskingMessageResponse:
    if response_code == 200:
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=json.dumps(response_data).encode("UTF8"),
        ))
        response.Success = True
    else:
        await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
            TaskID=taskData.Task.ID,
            Response=f"{response_data}".encode("UTF8"),
        ))
        response.TaskStatus = "Error: Ghostwriter Query Error"
        response.Success = False
    return response
