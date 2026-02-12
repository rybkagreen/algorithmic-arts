from .domain.company import Company
from .infrastructure.kafka.producers import CompanyEventProducer
from .infrastructure.repositories.company_repository import CompanyRepository


class CreateCompanyCommand:
    def __init__(
        self,
        company_repository: CompanyRepository,
        event_producer: CompanyEventProducer,
    ):
        self.company_repository = company_repository
        self.event_producer = event_producer

    async def execute(self, **kwargs) -> Company:
        # Создание агрегата
        company = Company.create(**kwargs)
        
        # Сохранение в репозиторий
        saved_company = await self.company_repository.save(company)
        
        # Отправка доменных событий
        for event in company._domain_events:
            await self.event_producer.produce_event(event)
        
        return saved_company