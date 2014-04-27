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
    def set_device_id(this, device_id):
        setting = DBSession.query(this).filter(
            this.name == "device_id"
        ).first()
        if setting:
            setting.value = device_id
            DBSession.add(setting)
        else:
            new_setting = this()
            new_setting.name = "device_id"
            new_setting.value = device_id
            DBSession.add(new_setting)
        DBSession.flush()

    @classmethod
    def get_device_id(this):
        device_id = DBSession.query(_settings).filter(
            _settings.name == "device_id"
        ).first()
        if device_id:
            return device_id.value
        return None


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
    artwork = Column(LargeBinary)

    artist_id = Column(Integer, ForeignKey("artist.id"))
    artist = relationship("Artist", backref="albums")


class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    genre = Column(Text)
    artwork = Column(LargeBinary)
