#!/usr/bin/env python3
"""
Demo script to simulate 2 complete Doppelkopf games with 4 players.

This script demonstrates the full game flow:
- User registration and login
- Group creation
- Playing complete games (10 tricks each)
- Marking ready and starting new games

Run with: python -m doko.json_api_client.demo_full_game
"""
import asyncio
import sys
import logging
from typing import List
from doko.json_api_client.client import AsyncDokoApiClient

# Disable debug logging from httpx and httpcore
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)


async def main():
    """Run the demo."""
    base_url = "http://localhost:8001"
    
    print("=" * 80)
    print("DOPPELKOPF FULL GAME SIMULATION")
    print("=" * 80)
    
    # Player names
    import time
    timestamp = int(time.time())
    usernames = [f"Alice{timestamp}", f"Bob{timestamp}", f"Charlie{timestamp}", f"Diana{timestamp}"]
    groupname = f"demo_{timestamp}"
    password = "demo123"
    
    print(f"\n📋 Setting up {len(usernames)} players: {', '.join(usernames)}")
    print(f"🎮 Group name: {groupname}")
    print(f"🌐 Server: {base_url}\n")
    
    # Step 1: Create and login users
    print("=" * 80)
    print("STEP 1: USER REGISTRATION & LOGIN")
    print("=" * 80)
    
    clients: List[AsyncDokoApiClient] = []
    
    try:
        for i, username in enumerate(usernames):
            client = AsyncDokoApiClient(base_url=base_url)
            
            # Register
            try:
                await client.create_user(username=username, password=password, password_validation=password)
                print(f"✅ User '{username}' registered")
            except Exception as e:
                print(f"ℹ️  User '{username}' already exists (skipping registration): {e}")
            
            # Login
            try:
                await client.login(username=username, password=password)
                print(f"🔐 User '{username}' logged in")
            except Exception as e:
                print(f"❌ Login failed for '{username}': {e}")
                raise
            
            clients.append(client)
        
        # Step 2: Create group
        print("\n" + "=" * 80)
        print("STEP 2: GROUP CREATION")
        print("=" * 80)
        
        try:
            group_response = await clients[0].create_group(
                groupname=groupname,
                username_0=usernames[1],
                username_1=usernames[2],
                username_2=usernames[3]
            )
            
            if group_response.get("success"):
                print(f"✅ Group '{groupname}' created by {usernames[0]}")
                print(f"   Members: {', '.join(usernames)}")
            else:
                print(f"ℹ️  Group response: {group_response}")
        except Exception as e:
            print(f"ℹ️  Group might already exist: {e}")
            print(f"   Continuing with existing group '{groupname}'...")
        
        # Play Game 1
        await play_game(clients, usernames, groupname, game_number=1)
        
        # Step: Mark ready for next game
        print("\n" + "=" * 80)
        print("PREPARING FOR GAME 2")
        print("=" * 80)
        
        print("\n🔄 Players marking ready for next game...")
        for i, (client, username) in enumerate(zip(clients, usernames)):
            await client.mark_ready_for_next_game(status="ready", groupname=groupname)
            print(f"   ✓ {username} is ready")
            await asyncio.sleep(0.2)
        
        await asyncio.sleep(0.5)  # Give time for game creation
        
        # Play Game 2
        await play_game(clients, usernames, groupname, game_number=2)
        
        print("\n" + "=" * 80)
        print("🎉 SIMULATION COMPLETE!")
        print("=" * 80)
        print(f"✅ Successfully played 2 complete games")
        print(f"✅ Total tricks: 20 (10 per game)")
        print(f"✅ Total cards played: 80 (40 per game)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        for client in clients:
            await client.close()
        print("✅ All connections closed")


async def play_game(clients: List[AsyncDokoApiClient], usernames: List[str], groupname: str, game_number: int):
    """Play a complete game."""
    print("\n" + "=" * 80)
    print(f"GAME {game_number}")
    print("=" * 80)
    
    # Wait for game to be created
    print(f"\n🎲 Starting game {game_number}...")
    
    game_id = None
    max_attempts = 20
    
    for attempt in range(max_attempts):
        for client in clients:
            response = await client.create_game(groupname=groupname)
            if response.get("success"):
                game_id = response["game_id"]
                break
        if game_id:
            break
        await asyncio.sleep(0.2)
    
    if not game_id:
        raise Exception(f"Failed to create/join game {game_number}")
    
    print(f"✅ Game {game_number} created (ID: {game_id[:8]}...)")
    
    # Show initial hands with full card details
    print(f"\n📇 Initial hands:")
    suit_symbols = {"hearts": "♥️", "diamonds": "♦️", "clubs": "♣️", "spades": "♠️"}
    
    for i, (client, username) in enumerate(zip(clients, usernames)):
        hand_response = await client.get_hand(game_id)
        cards = hand_response.get("cards", [])
        
        # Format each card nicely
        card_strings = []
        for card in cards:
            suit = card['suit']
            rank = card['rank']
            suit_symbol = suit_symbols.get(suit, suit)
            rank_display = rank.capitalize()
            card_strings.append(f"{rank_display} {suit_symbol}")
        
        cards_display = ", ".join(card_strings)
        print(f"   {username}: {cards_display}")
    
    # Play 10 tricks
    tricks_per_game = 10
    print(f"\n🃏 Playing {tricks_per_game} tricks...")
    
    for trick_num in range(tricks_per_game):
        print(f"\n  Trick {trick_num + 1}/10:")
        
        # Track cards played in this trick to determine winner display
        trick_plays = []
        
        # Play 4 cards (one per player)
        for card_num in range(4):
            # Find who should play
            current_player_idx = None
            playable_card = None
            
            for player_idx, client in enumerate(clients):
                hand_response = await client.get_hand(game_id)
                cards = hand_response.get("cards", [])
                
                playable_cards = [c for c in cards if c.get("playable", False)]
                if playable_cards:
                    current_player_idx = player_idx
                    playable_card = playable_cards[0]
                    break
            
            if current_player_idx is None:
                print("    ⚠️  No playable cards found")
                break
            
            # Play the card
            username = usernames[current_player_idx]
            suit = playable_card["suit"]
            rank = playable_card["rank"]
            
            await clients[current_player_idx].play_card(game_id, suit=suit, rank=rank)
            
            # Format card nicely
            suit_symbols = {"hearts": "♥️", "diamonds": "♦️", "clubs": "♣️", "spades": "♠️"}
            suit_symbol = suit_symbols.get(suit, suit)
            rank_display = rank.capitalize()
            
            print(f"    {username:10s} plays: {rank_display} {suit_symbol}")
            trick_plays.append((username, rank_display, suit_symbol))
        
        # After trick completes, show who won
        # Wait for the server to determine winner and create new trick
        # (Server has a 1 second sleep after trick completes)
        await asyncio.sleep(1.5)
        
        # Try to determine who won by checking who can play next
        # (The winner of the trick gets to play first in the next trick)
        if trick_num < 9:  # Not the last trick
            for idx, client in enumerate(clients):
                hand_response = await client.get_hand(game_id)
                cards = hand_response.get("cards", [])
                playable_cards = [c for c in cards if c.get("playable", False)]
                if playable_cards:
                    winner_name = usernames[idx]
                    print(f"    🏆 Winner: {winner_name}")
                    break
        
        # Small pause between tricks
        await asyncio.sleep(0.1)
    
    print(f"\n✅ Game {game_number} completed!")
    
    # Show game review
    review = await clients[0].get_game_review(game_id)
    game_num = review.get('game_number', review.get('gamenumber', '?'))
    print(f"   Game number in sitting: {game_num}")


if __name__ == "__main__":
    print("\n🚀 Starting Doppelkopf demo...")
    print("⚠️  Make sure the server is running on http://localhost:8001\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
