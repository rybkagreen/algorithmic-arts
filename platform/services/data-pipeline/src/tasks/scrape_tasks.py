from celery import current_app
from celery_app import celery_app
from ..scrapers.vc_ru import VCRuScraper
from ..scrapers.rusbase import RusbaseScraper
from ..scrapers.habr_career import HabrCareerScraper
from ..scrapers.crunchbase import CrunchbaseScraper
from ..load.kafka_producer import KafkaProducer
import structlog

log = structlog.get_logger()

# Инициализация зависимостей
kafka_producer = KafkaProducer()

@celery_app.task(name="src.tasks.scrape_tasks.scrape_vc_ru_task")
def scrape_vc_ru_task():
    """Скрапинг VC.ru."""
    try:
        scraper = VCRuScraper()
        companies = current_app.loop.run_until_complete(scraper.scrape())
        
        # Публикуем в Kafka
        for company in companies:
            current_app.loop.run_until_complete(
                kafka_producer.publish_company_raw(company)
            )
        
        return {"status": "success", "companies": len(companies)}
    except Exception as exc:
        log.error("vc_ru_scrape_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}

@celery_app.task(name="src.tasks.scrape_tasks.scrape_rusbase_task")
def scrape_rusbase_task():
    """Скрапинг Rusbase."""
    try:
        scraper = RusbaseScraper()
        companies = current_app.loop.run_until_complete(scraper.scrape())
        
        for company in companies:
            current_app.loop.run_until_complete(
                kafka_producer.publish_company_raw(company)
            )
        
        return {"status": "success", "companies": len(companies)}
    except Exception as exc:
        log.error("rusbase_scrape_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}

@celery_app.task(name="src.tasks.scrape_tasks.scrape_habr_career_task")
def scrape_habr_career_task():
    """Скрапинг Habr Career."""
    try:
        scraper = HabrCareerScraper()
        companies = current_app.loop.run_until_complete(scraper.scrape())
        
        for company in companies:
            current_app.loop.run_until_complete(
                kafka_producer.publish_company_raw(company)
            )
        
        return {"status": "success", "companies": len(companies)}
    except Exception as exc:
        log.error("habr_career_scrape_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}

@celery_app.task(name="src.tasks.scrape_tasks.scrape_crunchbase_task")
def scrape_crunchbase_task():
    """Скрапинг Crunchbase."""
    try:
        from ..config import settings
        scraper = CrunchbaseScraper(api_key=settings.CRUNCHBASE_API_KEY)
        companies = current_app.loop.run_until_complete(scraper.scrape())
        
        for company in companies:
            current_app.loop.run_until_complete(
                kafka_producer.publish_company_raw(company)
            )
        
        return {"status": "success", "companies": len(companies)}
    except Exception as exc:
        log.error("crunchbase_scrape_failed", error=str(exc))
        return {"status": "error", "error": str(exc)}