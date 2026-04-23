from app.models.major import Major
from app.models.major_university import MajorUniversity
from app.models.major_detail import MajorDetail
from app.models.user import User
from app.models.favorite import Favorite
from app.models.recommend_log import RecommendLog
from app.models.operation_log import OperationLog

__all__ = [
    "Major",
    "MajorUniversity",
    "MajorDetail",
    "User",
    "Favorite",
    "RecommendLog",
    "OperationLog",
]
