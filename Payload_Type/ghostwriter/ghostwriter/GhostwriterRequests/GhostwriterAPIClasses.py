import hmac
import hashlib
import base64
import requests
import datetime
import asyncio
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from graphql.error.graphql_error import GraphQLError
from mythic_container.logging import logger

from typing import Optional


class Credentials(object):
    def __init__(self, api_token: str) -> None:
        self.api_token = api_token


class GhostwriterClient(object):
    def __init__(self, url: str, credentials: Credentials) -> None:
        self._url = url
        self._credentials = credentials
        self.headers = {
            "User-Agent": f"Ghostwriter_Agent/1.0",
            "Authorization": f"Bearer {self._credentials.api_token}",
            "Content-Type": "application/json"
        }
        self.transport = AIOHTTPTransport(url=self._url, timeout=10, headers=self.headers)
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False, )
        self.session = None
        self.last_error = ""

    def __del__(self):
        asyncio.create_task(self.client.close_async())

    def _format_url(self, uri: str) -> str:
        formatted_uri = uri
        if uri.startswith("/"):
            formatted_uri = formatted_uri[1:]

        return f"{self._url}/{formatted_uri}"

    async def graphql_query(self, query: gql, variable_values: Optional[dict] = None) -> dict[str, any]:
        if self.session is None:
            self.session = await self.client.connect_async(reconnecting=True)
        # Perform the request with the signed and expected headers
        try:
            result = await self.session.execute(query, variable_values=variable_values)
            self.last_error = ""
            return result
        except TimeoutError:
            logger.error(
                "Timeout occurred while trying to connect to Ghostwriter at %s",
                self._url
            )
            self.last_error = "timeout trying to connect to Ghostwriter"
            return None
        except TransportQueryError as e:
            logger.exception("Error encountered while fetching GraphQL schema: %s", e)
            payload = e.errors[0]
            self.last_error = f"GraphQL error: {payload['message']}"
            if "extensions" in payload:
                if "code" in payload["extensions"]:
                    if payload["extensions"]["code"] == "access-denied":
                        logger.error(
                            "Access denied for the provided Ghostwriter API token! Check if it is valid, update your configuration, and restart")
                        self.last_error = f"Access denied for API token"
                    if payload["extensions"]["code"] == "postgres-error":
                        logger.error(
                            "Ghostwriter's database rejected the query! Check if your configured log ID is correct.")
                        self.last_error = f"Database error"
            return None
        except GraphQLError as e:
            logger.exception("Error with GraphQL query: %s", e)
            self.last_error = f"Graphql Error: {e}"
            return None
        except Exception as e:
            logger.exception(e)
            self.last_error = f"Unknown Error: {e}"
            return None
