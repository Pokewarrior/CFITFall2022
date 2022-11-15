import QueryTesting
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=QueryTesting.db_connection)
session=Session()
newEntry = QueryTesting.assessments(None,222,123,"idk","123idk","admin","Fall","dopey","derp",234,None)
session.add(newEntry)
session.commit()