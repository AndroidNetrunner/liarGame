import discord
from start_round import start_round

async def start_game(current_game):
  current_game.start = True
  assign_numbers(current_game)
  embed = discord.Embed(title="라이어 게임이 시작되었습니다!",
                       description="사용 방법을 설명드릴게요~")
  embed.add_field(name="라이어라면,",
	                value="제시어를 모르는 상태로, 마치 아는 척 연기해 남을 속여넘겨야 합니다. 제시어를 맞춰서 역전승해도 되고요!", inline=False)
  embed.add_field(
		name="시민이라면,", value="제시어가 주어질 거에요! 제시어를 모르는 라이어의 정체를 투표로 검거하면 승리하게 됩니다!", inline=False)
  for member in current_game.members:
    if member.dm_channel:
      channel = member.dm_channel
    elif member.dm_channel is None:
      channel = await member.create_dm()
    await channel.send(embed=embed)
  await start_round(current_game)


def assign_numbers(room_info):
    copied_players = room_info.members.copy()
    for emoji in room_info.emojis:
        if copied_players:
            room_info.emojis[emoji] = copied_players.pop(0)
        else:
            break