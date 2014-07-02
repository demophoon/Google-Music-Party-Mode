from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    LargeBinary,
    DateTime,

    ForeignKey,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class _settings(Base):
    __tablename__ = '_settings'
    name = Column(Text, primary_key=True)
    value = Column(Text)

    @classmethod
    def set_option(this, name, value):
        setting = DBSession.query(this).filter(
            this.name == name
        ).first() or this()
        setting.name = name
        setting.value = value
        DBSession.add(setting)
        DBSession.flush()

    @classmethod
    def get_option(this, name):
        setting = DBSession.query(_settings).filter(
            _settings.name == name
        ).first()
        if setting:
            return setting.value
        return None

    @classmethod
    def set_device_id(this, device_id):
        this.set_option("device_id", device_id)

    @classmethod
    def get_device_id(this):
        return this.get_option("device_id")


class PlayHistory(Base):
    __tablename__ = 'play_history'
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey("song.id"))
    created_at = Column(DateTime)
    action = Column(Text)


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    source = Column(Text)
    location = Column(Text)
    title = Column(Text)
    rating = Column(Float)
    track = Column(Integer)
    play_count = Column(Integer)
    duration = Column(Integer)

    album_id = Column(Integer, ForeignKey("album.id"))
    album = relationship("Album", backref="songs")


class Album(Base):
    __tablename__ = 'album'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    disc_number = Column(Integer)
    year = Column(Integer)
    album_artist = Column(Text)
    total_track_count = Column(Integer)
    artwork = Column(Text)

    artist_id = Column(Integer, ForeignKey("artist.id"))
    artist = relationship("Artist", backref="albums")


class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    genre = Column(Text)
    artwork = Column(LargeBinary)
