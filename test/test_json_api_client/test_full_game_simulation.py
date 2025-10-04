"""
Full game simulation tests.

This module simulates complete Doppelkopf games from start to finish:
- Create 4 users and log them in
- Create a group with all 4 players
- Start a game
- Play all 10 tricks (40 cards total) until the game ends
- Start a second game and play it through
"""

import pytest
from doko.json_api_client import DokoApiClient
from doko.json_api_client.client import AsyncDokoApiClient
from typing import List, Dict, Any


def create_and_login_users(base_url: str, usernames: List[str], password: str = "testpass123") -> List[DokoApiClient]:
    """
    Create multiple users and return authenticated clients.
    
    Args:
        base_url: Base URL for the API
        usernames: List of usernames to create
        password: Password for all users
        
    Returns:
        List of authenticated DokoApiClient instances
    """
    clients = []
    
    for username in usernames:
        # Create a new client for this user
        client = DokoApiClient(base_url=base_url)
        
        # Create the user
        try:
            client.create_user(
                username=username,
                password=password,
                password_validation=password
            )
        except Exception:
            # User might already exist from previous test run, that's ok
            pass
        
        # Login the user
        client.login(username, password)
        clients.append(client)
    
    return clients


def play_full_game(clients: List[DokoApiClient], game_id: str) -> None:
    """
    Play a full Doppelkopf game (10 tricks, 40 cards).
    
    Args:
        clients: List of 4 authenticated clients (one per player)
        game_id: ID of the game to play
    """
    assert len(clients) == 4, "Need exactly 4 players for Doppelkopf"
    
    # Play 10 tricks (each player plays 10 cards total)
    for trick_num in range(10):
        print(f"\n--- Trick {trick_num + 1} ---")
        
        # 4 cards per trick
        for card_in_trick in range(4):
            # Find which player should play next by checking who has playable cards
            current_player_idx = None
            for player_idx, client in enumerate(clients):
                hand_response = client.get_hand(game_id)
                cards = hand_response.get("cards", [])
                
                # Check if this player has any playable cards
                playable_cards = [c for c in cards if c.get("playable", False)]
                if playable_cards:
                    current_player_idx = player_idx
                    card = playable_cards[0]  # Play the first playable card
                    break
            
            if current_player_idx is None:
                # Debug: print all hands to see what's happening
                print(f"\n⚠️  No player has playable cards - checking hands:")
                for pidx, client in enumerate(clients):
                    hand_resp = client.get_hand(game_id)
                    cards = hand_resp.get("cards", [])
                    print(f"  Player {pidx}: {len(cards)} cards, playable={[c.get('playable', False) for c in cards]}")
                print(f"  Trick {trick_num + 1}, Card {card_in_trick + 1}/4")
                raise Exception("Game stopped unexpectedly - no playable cards!")
            
            # Play the card
            suit = card["suit"]
            rank = card["rank"]
            
            print(f"Player {current_player_idx} plays: {rank} of {suit}")
            
            try:
                play_response = clients[current_player_idx].play_card(game_id, suit=suit, rank=rank)
                if "warning" in play_response:
                    print(f"  Warning: {play_response['warning']}")
                else:
                    print(f"  Card played successfully")
            except Exception as e:
                print(f"  Error playing card: {e}")
                # Get more details about the game state
                try:
                    game_state = clients[current_player_idx].get_game(game_id)
                    print(f"  Game state: {game_state}")
                except Exception as e2:
                    print(f"  Could not get game state: {e2}")
                raise


async def play_full_game_async(clients: List[AsyncDokoApiClient], game_id: str) -> None:
    """
    Play a full Doppelkopf game (10 tricks, 40 cards) asynchronously.
    
    Args:
        clients: List of 4 authenticated async clients (one per player)
        game_id: ID of the game to play
    """
    assert len(clients) == 4, "Need exactly 4 players for Doppelkopf"
    
    # Play 10 tricks (each player plays 10 cards total)
    for trick_num in range(10):
        print(f"\n--- Trick {trick_num + 1} ---")
        
        # 4 cards per trick
        for card_in_trick in range(4):
            # Find which player should play next by checking who has playable cards
            current_player_idx = None
            for player_idx, client in enumerate(clients):
                hand_response = await client.get_hand(game_id)
                cards = hand_response.get("cards", [])
                
                # Check if this player has any playable cards
                playable_cards = [c for c in cards if c.get("playable", False)]
                if playable_cards:
                    current_player_idx = player_idx
                    card = playable_cards[0]  # Play the first playable card
                    break
            
            if current_player_idx is None:
                # Debug: print all hands to see what's happening
                print(f"\n⚠️  No player has playable cards - checking hands:")
                for pidx, client in enumerate(clients):
                    hand_resp = await client.get_hand(game_id)
                    cards = hand_resp.get("cards", [])
                    print(f"  Player {pidx}: {len(cards)} cards, playable={[c.get('playable', False) for c in cards]}")
                print(f"  Trick {trick_num + 1}, Card {card_in_trick + 1}/4")
                raise Exception("Game stopped unexpectedly - no playable cards!")
            
            # Play the card
            suit = card["suit"]
            rank = card["rank"]
            
            print(f"Player {current_player_idx} plays: {rank} of {suit}")
            
            try:
                play_response = await clients[current_player_idx].play_card(game_id, suit=suit, rank=rank)
                if "warning" in play_response:
                    print(f"  Warning: {play_response['warning']}")
                else:
                    print(f"  Card played successfully")
            except Exception as e:
                print(f"  Error playing card: {e}")
                # Get more details about the game state
                try:
                    game_state = await clients[current_player_idx].get_game(game_id)
                    print(f"  Game state: {game_state}")
                except Exception as e2:
                    print(f"  Could not get game state: {e2}")
                raise


class TestFullGameSimulationSync:
    """Test complete game simulations with sync clients."""
    
    def test_two_complete_games(self, test_server):
        """Simulate 2 complete games from start to finish."""
        usernames = ["player1_sim", "player2_sim", "player3_sim", "player4_sim"]
        groupname = "fullgame_sync"
        
        # Step 1: Create and login 4 users
        print("\n=== Creating and logging in 4 users ===")
        clients = create_and_login_users(test_server.base_url, usernames)
        
        try:
            # Step 2: Create a group with all 4 players
            print("\n=== Creating group ===")
            group_response = clients[0].create_group(
                groupname=groupname,
                username_0=usernames[1],
                username_1=usernames[2],
                username_2=usernames[3]
            )
            print(f"Group created: {group_response}")
            assert group_response["success"] is True
            
            # Step 3: All players create/join the game
            print("\n=== Starting first game ===")
            import time
            
            # Have all players mark themselves as waiting
            for i, client in enumerate(clients):
                print(f"Player {i} ({usernames[i]}) joining game...")
                response = client.create_game(groupname=groupname)
                print(f"  Response: {response}")
                time.sleep(0.3)  # Small delay to avoid race conditions
            
            # The last player triggers game creation, so poll to get the game_id
            print("\n=== Polling for game creation ===")
            game_id = None
            max_polls = 20
            for poll in range(max_polls):
                for i, client in enumerate(clients):
                    response = client.create_game(groupname=groupname)
                    if response.get("success"):
                        game_id = response["game_id"]
                        print(f"Game created! Game ID: {game_id}")
                        break
                if game_id:
                    break
                time.sleep(0.2)
            
            assert game_id is not None, "Game should have been created"
            print(f"\nGame ID: {game_id}")
            
            # Step 4: Play the first game to completion
            print("\n=== Playing first game (10 tricks) ===")
            play_full_game(clients, game_id)
            
            print("\n=== First game completed! ===")
            
            # Step 5: Get game review
            print("\n=== Checking game review ===")
            for i, client in enumerate(clients):
                review = client.get_game_review(game_id)
                print(f"Player {i} review: Game {review.get('gamenumber')}, All ready: {review.get('all_ready')}")
            
            # Step 6: All players mark ready for next game
            print("\n=== Players marking ready for next game ===")
            for i, client in enumerate(clients):
                ready_response = client.mark_ready_for_next_game(
                    status="ready",
                    groupname=groupname
                )
                print(f"Player {i} ready: {ready_response}")
                time.sleep(0.3)  # Give time for game creation
            
            # Small delay to ensure game is created by the leader
            time.sleep(0.5)
            
            # Step 7: Get the second game ID (game was created during ready calls)
            print("\n=== Getting second game ID ===")
            game_id_2 = None
            for i, client in enumerate(clients):
                print(f"Player {i} checking for new game...")
                response = client.create_game(groupname=groupname)
                print(f"  Response: {response}")
                if response.get("success"):
                    game_id_2 = response["game_id"]
                    break
            
            assert game_id_2 is not None, "Second game should have been created"
            assert game_id_2 != game_id, f"Second game should have different ID (first: {game_id}, second: {game_id_2})"
            print(f"\nSecond Game ID: {game_id_2}")
            
            # Step 8: Play the second game to completion
            print("\n=== Playing second game (10 tricks) ===")
            play_full_game(clients, game_id_2)
            
            print("\n=== Second game completed! ===")
            
            # Step 9: Verify final game review
            print("\n=== Checking final game review ===")
            final_review = clients[0].get_game_review(game_id_2)
            game_number = final_review.get('game_number', final_review.get('gamenumber'))
            print(f"Final review: Game {game_number}")
            assert game_number == 1, f"Second game should be game number 1 (0-indexed), got {game_number}"
            
            print("\n=== Test completed successfully! ===")
            
        finally:
            # Cleanup: close all clients
            for client in clients:
                client.close()


class TestFullGameSimulationAsync:
    """Test complete game simulations with async clients."""
    
    async def test_two_complete_games(self, test_server):
        """Simulate 2 complete games from start to finish using async clients."""
        usernames = ["player1_async", "player2_async", "player3_async", "player4_async"]
        groupname = "fullgame_async"
        password = "testpass123"
        
        # Step 1: Create and login 4 users
        print("\n=== Creating and logging in 4 async users ===")
        clients = []
        
        for username in usernames:
            client = AsyncDokoApiClient(base_url=test_server.base_url)
            
            # Create user
            try:
                await client.create_user(
                    username=username,
                    password=password,
                    password_validation=password
                )
            except Exception:
                # User might already exist
                pass
            
            # Login
            await client.login(username, password)
            clients.append(client)
        
        try:
            # Step 2: Create a group
            print("\n=== Creating group ===")
            group_response = await clients[0].create_group(
                groupname=groupname,
                username_0=usernames[1],
                username_1=usernames[2],
                username_2=usernames[3]
            )
            print(f"Group created: {group_response}")
            assert group_response["success"] is True
            
            # Step 3: All players create/join the game
            print("\n=== Starting first game ===")
            import asyncio
            
            # Have all players mark themselves as waiting
            for i, client in enumerate(clients):
                print(f"Player {i} ({usernames[i]}) joining game...")
                response = await client.create_game(groupname=groupname)
                print(f"  Response: {response}")
                await asyncio.sleep(0.3)  # Small delay to avoid race conditions
            
            # The last player triggers game creation, so poll to get the game_id
            print("\n=== Polling for game creation ===")
            game_id = None
            max_polls = 20
            for poll in range(max_polls):
                for i, client in enumerate(clients):
                    response = await client.create_game(groupname=groupname)
                    if response.get("success"):
                        game_id = response["game_id"]
                        print(f"Game created! Game ID: {game_id}")
                        break
                if game_id:
                    break
                await asyncio.sleep(0.2)
            
            assert game_id is not None, "Game should have been created"
            print(f"\nGame ID: {game_id}")
            
            # Step 4: Play the first game to completion
            print("\n=== Playing first game (10 tricks) ===")
            await play_full_game_async(clients, game_id)
            
            print("\n=== First game completed! ===")
            
            # Step 5: Get game review
            print("\n=== Checking game review ===")
            for i, client in enumerate(clients):
                review = await client.get_game_review(game_id)
                print(f"Player {i} review: Game {review.get('gamenumber')}, All ready: {review.get('all_ready')}")
            
            # Step 6: All players mark ready for next game
            print("\n=== Players marking ready for next game ===")
            for i, client in enumerate(clients):
                ready_response = await client.mark_ready_for_next_game(
                    status="ready",
                    groupname=groupname
                )
                print(f"Player {i} ready: {ready_response}")
                await asyncio.sleep(0.3)  # Give time for game creation
            
            # Small delay to ensure game is created by the last player
            await asyncio.sleep(0.5)
            
            # Step 7: Get the second game ID (game was created during ready calls)
            print("\n=== Getting second game ID ===")
            game_id_2 = None
            for i, client in enumerate(clients):
                print(f"Player {i} checking for new game...")
                response = await client.create_game(groupname=groupname)
                print(f"  Response: {response}")
                if response.get("success"):
                    game_id_2 = response["game_id"]
                    break
            
            assert game_id_2 is not None, "Second game should have been created"
            assert game_id_2 != game_id, f"Second game should have different ID (first: {game_id}, second: {game_id_2})"
            print(f"\nSecond Game ID: {game_id_2}")
            
            # Step 8: Play the second game to completion
            print("\n=== Playing second game (10 tricks) ===")
            await play_full_game_async(clients, game_id_2)
            
            print("\n=== Second game completed! ===")
            
            # Step 9: Verify final game review
            print("\n=== Checking final game review ===")
            final_review = await clients[0].get_game_review(game_id_2)
            game_number = final_review.get('game_number', final_review.get('gamenumber'))
            print(f"Final review: Game {game_number}")
            assert game_number == 1, f"Second game should be game number 1 (0-indexed), got {game_number}"
            
            print("\n=== Async test completed successfully! ===")
            
        finally:
            # Cleanup: close all clients
            for client in clients:
                await client.close()
