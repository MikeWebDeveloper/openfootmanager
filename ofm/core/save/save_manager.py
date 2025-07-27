#      Openfoot Manager - A free and open source soccer management simulation
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ..db.models import SaveGame, SaveType
from .serializer import SaveSerializer


class SaveManager:
    """Manages game saves including creation, loading, and deletion"""

    # Current game version
    GAME_VERSION = "0.1.0"

    # Maximum number of autosaves to keep
    MAX_AUTOSAVES = 5

    def __init__(self, session: Session, save_directory: Optional[str] = None):
        self.session = session
        self.serializer = SaveSerializer(session)

        # Set up save directory
        if save_directory:
            self.save_dir = Path(save_directory)
        else:
            # Default to user's home directory
            self.save_dir = Path.home() / "OpenFootManager" / "saves"

        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def create_save(
        self,
        name: str,
        manager_name: str,
        club_id: str,
        current_date: datetime,
        save_type: SaveType = SaveType.MANUAL,
        play_time: int = 0,
        metadata: Optional[Dict] = None
    ) -> SaveGame:
        """
        Create a new save game

        Args:
            name: Name of the save
            manager_name: Name of the manager
            club_id: ID of the managed club
            current_date: Current game date
            save_type: Type of save (manual, autosave, etc.)
            play_time: Total playtime in seconds
            metadata: Additional metadata to store

        Returns:
            Created SaveGame object
        """
        # Extract current game state
        game_state = self.serializer.extract_current_game_state()

        # Add manager info to game state
        game_state['manager'] = {
            'name': manager_name,
            'club_id': club_id,
            'current_date': current_date.isoformat(),
            'play_time': play_time
        }

        # Serialize the game state
        compressed_state = self.serializer.serialize_game_state(game_state)

        # Create save game record
        save_game = SaveGame(
            name=name,
            save_type=save_type,
            game_version=self.GAME_VERSION,
            save_version=SaveSerializer.SAVE_VERSION,
            current_date=current_date,
            manager_name=manager_name,
            club_id=club_id,
            play_time=play_time,
            game_state=compressed_state,
            save_metadata=metadata or {}
        )

        self.session.add(save_game)
        self.session.commit()

        # Clean up old autosaves if needed
        if save_type == SaveType.AUTOSAVE:
            self._cleanup_old_autosaves()

        return save_game

    def load_save(self, save_id: int) -> Dict:
        """
        Load a save game

        Args:
            save_id: ID of the save to load

        Returns:
            Game state dictionary
        """
        save_game = self.session.get(SaveGame, save_id)
        if not save_game:
            raise ValueError(f"Save game with ID {save_id} not found")

        # Check version compatibility
        if save_game.save_version > SaveSerializer.SAVE_VERSION:
            raise ValueError(
                f"Save file version {save_game.save_version} is newer than "
                f"supported version {SaveSerializer.SAVE_VERSION}"
            )

        # Deserialize the game state
        game_state = self.serializer.deserialize_game_state(save_game.game_state)

        # Restore to database
        self.serializer.restore_game_state(game_state)

        # Return manager info for the game to use
        return game_state.get('manager', {})

    def list_saves(self, save_type: Optional[SaveType] = None) -> List[SaveGame]:
        """
        List all available saves

        Args:
            save_type: Filter by save type (optional)

        Returns:
            List of SaveGame objects
        """
        query = self.session.query(SaveGame)

        if save_type:
            query = query.filter_by(save_type=save_type)

        return query.order_by(SaveGame.last_modified.desc()).all()

    def delete_save(self, save_id: int) -> None:
        """Delete a save game"""
        save_game = self.session.get(SaveGame, save_id)
        if save_game:
            self.session.delete(save_game)
            self.session.commit()

    def update_save(
        self,
        save_id: int,
        current_date: datetime,
        play_time: int,
        metadata: Optional[Dict] = None
    ) -> SaveGame:
        """
        Update an existing save (for overwriting)

        Args:
            save_id: ID of the save to update
            current_date: Current game date
            play_time: Total playtime in seconds
            metadata: Additional metadata to store

        Returns:
            Updated SaveGame object
        """
        save_game = self.session.get(SaveGame, save_id)
        if not save_game:
            raise ValueError(f"Save game with ID {save_id} not found")

        # Extract current game state
        game_state = self.serializer.extract_current_game_state()

        # Add manager info to game state
        game_state['manager'] = {
            'name': save_game.manager_name,
            'club_id': save_game.club_id,
            'current_date': current_date.isoformat(),
            'play_time': play_time
        }

        # Update save game
        save_game.current_date = current_date
        save_game.play_time = play_time
        save_game.game_state = self.serializer.serialize_game_state(game_state)

        if metadata:
            save_game.save_metadata = metadata

        self.session.commit()

        return save_game

    def create_autosave(
        self,
        manager_name: str,
        club_id: str,
        current_date: datetime,
        play_time: int = 0,
        metadata: Optional[Dict] = None
    ) -> SaveGame:
        """Create an autosave"""
        # Generate autosave name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"Autosave_{timestamp}"

        return self.create_save(
            name=name,
            manager_name=manager_name,
            club_id=club_id,
            current_date=current_date,
            save_type=SaveType.AUTOSAVE,
            play_time=play_time,
            metadata=metadata
        )

    def export_save(self, save_id: int, export_path: str) -> None:
        """
        Export a save to an external file

        Args:
            save_id: ID of the save to export
            export_path: Path where to export the save
        """
        save_game = self.session.get(SaveGame, save_id)
        if not save_game:
            raise ValueError(f"Save game with ID {save_id} not found")

        # Create export data
        export_data = {
            'game_version': save_game.game_version,
            'save_version': save_game.save_version,
            'name': save_game.name,
            'manager_name': save_game.manager_name,
            'club_id': save_game.club_id,
            'current_date': save_game.current_date.isoformat(),
            'created_at': save_game.created_at.isoformat(),
            'play_time': save_game.play_time,
            'metadata': save_game.save_metadata,
            'game_state': save_game.game_state
        }

        # Write to file
        import json
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)

    def import_save(self, import_path: str, name: Optional[str] = None) -> SaveGame:
        """
        Import a save from an external file

        Args:
            import_path: Path to the save file to import
            name: Optional name for the imported save

        Returns:
            Imported SaveGame object
        """
        import json

        with open(import_path, 'r') as f:
            import_data = json.load(f)

        # Create new save game
        save_game = SaveGame(
            name=name or import_data['name'],
            save_type=SaveType.MANUAL,
            game_version=import_data['game_version'],
            save_version=import_data['save_version'],
            current_date=datetime.fromisoformat(import_data['current_date']),
            manager_name=import_data['manager_name'],
            club_id=import_data['club_id'],
            play_time=import_data.get('play_time', 0),
            game_state=import_data['game_state'],
            save_metadata=import_data.get('metadata', {})
        )

        self.session.add(save_game)
        self.session.commit()

        return save_game

    def _cleanup_old_autosaves(self) -> None:
        """Remove old autosaves beyond the maximum limit"""
        autosaves = self.session.query(SaveGame).filter_by(
            save_type=SaveType.AUTOSAVE
        ).order_by(SaveGame.created_at.desc()).all()

        # Delete excess autosaves
        for save in autosaves[self.MAX_AUTOSAVES:]:
            self.session.delete(save)

        self.session.commit()

    def get_save_info(self, save_id: int) -> Dict:
        """Get information about a save without loading it"""
        save_game = self.session.get(SaveGame, save_id)
        if not save_game:
            raise ValueError(f"Save game with ID {save_id} not found")

        return {
            'id': save_game.id,
            'name': save_game.name,
            'save_type': save_game.save_type.value,
            'manager_name': save_game.manager_name,
            'club_id': save_game.club_id,
            'current_date': save_game.current_date,
            'created_at': save_game.created_at,
            'last_modified': save_game.last_modified,
            'play_time': save_game.play_time,
            'game_version': save_game.game_version,
            'save_version': save_game.save_version,
            'metadata': save_game.save_metadata
        }
