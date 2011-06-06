from sqlalchemy import *
from migrate import *

metadata = MetaData()

blueprint_zid = Column('blueprint_zid', Integer, nullable=True, unique=False)
inventory_date = Column('inventory_date', Date)

terms = [
    dict(vocabulary_name='aliquot_state', title=u'Inaccurate Data', token=u'incorrect', value=u'incorrect'),
    dict(vocabulary_name='aliquot_state', title=u'Check Out', token=u'pending - checkout', value=u'pending - checkout'),
    dict(vocabulary_name='aliquot_state', title=u'Hold in Queue', token=u'queued', value=u'queued'),
    ]

def upgrade(migrate_engine):
    """ Introduces new changes to the specimen/aliquot/terms table necessary
        for inventory processing.
    """
    metadata.bind = migrate_engine

    specimen_table = Table('specimen', metadata, autoload=True)
    aliquot_table = Table('aliquot', metadata, autoload=True)
    vocabulary_table = Table('specimen_aliquot_term', metadata, autoload=True)

    blueprint_zid.create(specimen_table)
    inventory_date.create(aliquot_table)

    metadata.bind.execute(vocabulary_table.insert(), terms)


def downgrade(migrate_engine):
    metadata.bind = migrate_engine

    specimen_table = Table('specimen', metadata, autoload=True)
    aliquot_table = Table('aliquot', metadata, autoload=True)
    vocabulary_table = Table('specimen_aliquot_term', metadata, autoload=True)

    blueprint_zid.drop(specimen_table)
    inventory_date.drop(specimen_table)

    tokens = [t['token'] for t in terms]

    query = (
        vocabulary_table.delete()
        .where(
            (vocabulary_table.c.vocabulary_name == 'aliquot_state') &
            (vocabulary_table.c.token.in_(tokens))
            )
        )

    metadata.bind.execute(query)

