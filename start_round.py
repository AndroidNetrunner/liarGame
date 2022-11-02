import random
import discord
from discord import Color
from game_data import active_game

async def start_round(current_game):
    await reset_round(current_game)
    if current_game.current_round >= current_game.round:
        return await show_result(current_game)
    await notify_role_to_players(current_game)
    await send_vote(current_game)

async def reset_round(current_game):
    current_game.liar = random.choice(current_game.members)
    current_game.word = random.choice(current_game.words)
    current_game.vote = {}
    while current_game.word in current_game.already:
        current_game.word = random.choice(current_game.words)
    current_game.already.add(current_game.word)

async def show_result(current_game):
    del active_game[current_game.main_channel.channel.id]
    embed = discord.Embed(title="모든 게임이 종료되었습니다!", description=f"{current_game.round}개의 문제 중 {current_game.correct}개의 정답을 맞추셨습니다.")
    await current_game.main_channel.send(embed=embed)

async def notify_role_to_players(current_game):
    for member in current_game.members:
        if member == current_game.liar:
            embed = discord.Embed(title="당신은 이번 라운드의 라이어입니다.",
                                    description="힌트 제공자들이 힌트를 줄 동안 잠시만 기다려주세요~",
                                    color=Color.red())
        else:
            embed = discord.Embed(title="당신은 이번 라운드의 시민입니다.",
                                    description=f"제시어 : {current_game.word}",
                                    color=Color.blue())
        await member.dm_channel.send(embed=embed)

async def send_vote(current_game):
  player_emojis = ""
  for emoji in current_game.emojis:
        player_emojis += f"{emoji} : {current_game.emojis[emoji]}\n" if current_game.emojis[emoji] else ""  
  for player in current_game.players:
    embed = discord.Embed(title="라이어가 누구인지 지목해주세요!",
                          description=f"아래 이모티콘을 통해 지목할 수 있습니다.")
    embed.add_field(name="각 이모티콘이 의미하는 플레이어는 다음과 같습니다.",
                    value=f"{player_emojis}\n")
    message = await player.send(embed=embed)
    current_game.vote_message[player.user_id] = message
  for emoji in current_game.emojis:
        if current_game.emojis[emoji]:
            await message.add_reaction(emoji)

async def vote(payload, current_game, lock):
  await lock.acquire()
  for member in current_game.members:
    if member.id == payload.user_id:
      player = member  
  await player.send("투표가 완료되었습니다.")
  emoji = str(payload.emoji)
  target = current_game.emojis[emoji]
  if emoji not in current_game.vote:
    current_game.vote[target.user_id] = 1
  else:
    current_game.vote[target.user_id] += 1
  await current_game.vote_message[player.user_id].delete()
  del current_game.vote_message[player.user_id]
  if not current_game.vote_message:
    await reveal_vote(current_game)
  await lock.release()

async def reveal_vote(current_game):
  nominated = (None, 0)
  for member in current_game.members:
    if nominated[0] == None:
      nominated = (member, current_game.vote[member.id])
    else:
      if nominated[1] == current_game.vote[member.id]:
        embed = discord.Embed(title="투표에서 동수표가 발생했습니다.",description="1명의 최다 득표자가 나올 때까지 재투표를 진행합니다.")
        await current_game.main_channel.send(embed=embed)
        current_game.vote = {}
        current_game.vote_message = {}
        await send_vote(current_game)
        return
      if nominated[1] == current_game.vote[member.id]:
        nominated = (member, current_game.vote[member.id])
  embed = discord.Embed(title="모든 플레이어가 투표를 끝냈습니다!")
  embed.add_field(name="가장 많이 투표를 받은 사람은...", value=f"{nominated[1]}입니다!")
  embed.add_field(name=f"그리고 스파이 검거에...", value="성공했습니다!" if nominated[1].id == current_game.liar.id else "실패했습니다...")
  await current_game.main_channel.send(embed=embed)
  current_game.round -= 1
  if current_game.round:
    await start_round(current_game)