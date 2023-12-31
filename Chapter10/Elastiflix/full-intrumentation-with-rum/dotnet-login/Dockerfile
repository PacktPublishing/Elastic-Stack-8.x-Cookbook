FROM ${ARCH}mcr.microsoft.com/dotnet/aspnet:7.0. AS base
WORKDIR /app
EXPOSE 8000

FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0-preview AS build
WORKDIR /src
COPY ["login.csproj", "./"]
RUN dotnet restore "./login.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "login.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "login.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

ARG AGENT_VERSION=1.22.0

RUN apt-get update && apt-get install -y zip curl
RUN curl -L -o ElasticApmAgent_${AGENT_VERSION}.zip https://github.com/elastic/apm-agent-dotnet/releases/download/v${AGENT_VERSION}/ElasticApmAgent_${AGENT_VERSION}.zip && unzip ElasticApmAgent_${AGENT_VERSION}.zip -d /elastic_apm_agent

ENV DOTNET_STARTUP_HOOKS=/elastic_apm_agent/ElasticApmAgentStartupHook.dll
ENV ELASTIC_APM_SERVICE_NAME=dotNetLoginService
ENV ELASTIC_APM_ENVIRONMENT=production

ENTRYPOINT ["dotnet", "login.dll"]
