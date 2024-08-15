from dependency_injector import containers, providers
from common.serialization import JsonSerializer, JsonDeserializer
from web.api.containers.files import FileControllerContainer


class ControllersContainer(containers.DeclarativeContainer):
    """Заранее сконфигурированный контейнер контроллеров"""

    config = providers.Configuration()
    database = providers.DependenciesContainer()
    storage = providers.DependenciesContainer()
    json_serializer = providers.Dependency(instance_of=JsonSerializer)
    json_deserializer = providers.Dependency(instance_of=JsonDeserializer)

    sub_containers = providers.Dict(
        files=providers.Container(
            FileControllerContainer,
            database=database,
            storage=storage,),
    )
