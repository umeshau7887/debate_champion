import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from agents.generic_debater import AbstractDebater, Debater, DebaterFactory
from data_model import DebateRound, DebateSession, DebateTurn

class DebateEngine:
    def __init__(self, motion: str, total_rounds: int, words_count_turn: int, age: int):
        self.session = DebateSession(
            motion=motion,
            total_rounds=total_rounds,
        )
        self.words_count_turn = words_count_turn
        self.session_agents = [
            DebaterFactory.create_debater(Debater.FOR_THE_MOTION),  
            DebaterFactory.create_debater(Debater.AGAINST_THE_MOTION)]   
        self.age = age  # Store the age for potential use in prompts or logic

    # async def get_agent_response(self, agent: DebateAgent) -> str:
    #     """Placeholder for your LLM call logic."""
    #     # Mix the session.motion and session.rounds (history) here for context
    #     return f"Mock response from {agent.name} defending {agent.stance}."

    async def run_debate(self):
        """Main execution loop that advances rounds and turns."""
        print(f"Starting debate on motion: '{self.session.motion}'\n")

        while self.session.current_round <= self.session.total_rounds:
            print(f"--- Starting Round {self.session.current_round} ---")
            current_round_obj = DebateRound(round_number=self.session.current_round)

            self.session.rounds.append(current_round_obj)

            # Iterates through agents sequentially (Proposition then Opposition)
            for agent in self.session_agents:
                print(f"Generating argument for: {agent.name}")
                
                # Fetch LLM text output
                argument_text = await agent.debate_on_the_motion(self.session.motion, self.words_count_turn, self.age, self.session.rounds, self.session.current_round, self.session.total_rounds)
                
                # Structure the turn and append to current round
                turn = DebateTurn(
                    agent_id=agent.name,
                    argument=argument_text
                )
                current_round_obj.turns.append(turn)

            
            self.session.current_round += 1

        self.session.is_completed = True
        print("\nDebate concluded successfully.")
        return self.session
