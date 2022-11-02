import asyncio
from asyncio.locks import Lock
import discord
import datetime
from discord.ext import commands
from utils import find_game_of_this_channel
from game_data import game_data, active_game
from guess import correct_answer, submit_guess, wrong_answer
from start_game import start_game
from hints import check_hints, give_hint
from start_round import vote

token = open("token.txt",
             'r').read()
game = discord.Game("도움말은 &help 입력")
bot = commands.Bot(command_prefix='&',
                   status=discord.Status.online, activity=game)

lock_for_vote = Lock()

def start_new_game(ctx):
    print(f"Liar game - {datetime.datetime.now()} : <start> {ctx.channel.id}")
    current_game = game_data()
    active_game[ctx.channel.id] = current_game
    current_game.main_channel = ctx
    current_game.starter = ctx.message.author
    current_game.members.append(current_game.starter)
    current_game.start = True
    current_game.can_join = True
    
@bot.command()
async def 시작(ctx):
    if ctx.channel.id in active_game:
        await ctx.send("이미 시작한 게임이 존재합니다.")
        return
    start_new_game(ctx)
    embed = discord.Embed(title="라이어 게임에 오신 것을 환영합니다!",
                          desciption="라이어 게임은 제시어를 모르는 숨겨진 라이어를 찾아야 하는 게임입니다.")
    embed.add_field(
        name="참가 방법", value="게임에 참가하고 싶다면 &참가를 입력해주세요.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def 리셋(ctx):
    if ctx.channel.id in active_game:
        del active_game[ctx.channel.id]
        await ctx.send("게임이 초기화되었습니다.")
    else:
        await ctx.send("시작한 게임이 존재하지 않습니다.")

@bot.command()
async def 참가(ctx):
    if ctx.channel.id not in active_game:
        await ctx.send("현재 시작한 게임이 없습니다.")
        return
    current_game = active_game[ctx.channel.id]
    if not current_game.can_join:
        await ctx.send("참가가 이미 마감되었습니다.")
        return
    player = ctx.message.author
    if player not in current_game.members:
        current_game.members.append(player)
        await ctx.send("{}님이 참가하셨습니다. 현재 플레이어 {}명".format(player.name, len(current_game.members)))
    else:
        await ctx.send("{}님은 이미 참가중입니다.".format(player.name))

@bot.command()
async def 마감(ctx):
    current_game = active_game[ctx.channel.id]
    if len(current_game.members) < 3:
        await ctx.send("플레이어 수가 2명 이하입니다. 게임을 시작할 수 없습니다.")
        return
    if not current_game.round:
        await ctx.send("문제의 개수가 0개입니다. 단어 개수를 설정해주세요.")
        return
    if current_game.can_join:
        current_game.can_join = False
        await ctx.send("참가가 마감되었습니다.")
        await start_game(current_game)
    else:
        await ctx.send("현재 진행중인 게임이 없습니다.")

@bot.command()
async def 라운드(ctx, number):
    current_game = active_game[ctx.channel.id]
    if current_game.can_join:
        current_game.round = int(number)
        await ctx.send(f'라운드 수가 {current_game.round}로 설정되었습니다.')
    else:
        await ctx.send("게임을 시작한 이후에는 라운드 수를 변경할 수 없습니다.")

@bot.event
async def on_raw_reaction_add(payload):
    current_game = find_game_of_this_channel(active_game, payload.user_id)
    if not current_game:
        return
    if str(payload.emoji) in current_game.emojis:
       asyncio.ensure_future(vote(payload, current_game, lock_for_vote))
    confirmer = current_game.members[1] if current_game.starter == current_game.guesser else current_game.starter
    if confirmer.id != payload.user_id:
        return
    await correct_answer(current_game) if str(payload.emoji) == "⭕" else await wrong_answer(current_game);

# @bot.event
# async def on_raw_reaction_add(payload):
#     current_game = get_current_game(payload.user_id)
#     room_info = current_game['game_room'] if current_game else None
#     game_status = current_game['game_status'] if current_game and 'game_status' in current_game else None
#     if not (room_info and game_status):
#         return
#     current_round = game_status.round_info
#     if str(payload.emoji) in room_info.emojis and room_info.emojis[str(payload.emoji)]:
#         await judge_merlin(payload, current_game) if game_status.assassination else await add_teammate(payload, room_info.emojis[str(payload.emoji)], current_game)          
#     elif str(payload.emoji) in ["👍","👎"]:
#         asyncio.ensure_future(vote(current_game, current_round, payload, lock_for_vote))
#     elif str(payload.emoji) in ["⭕", "❌"]:
#         asyncio.ensure_future(try_mission(payload, current_round['team'], current_game, lock_for_mission))



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.message.content} 는 존재하지 않는 명령어입니다.")
    else:
        await ctx.send("오류가 발생하였습니다. ~리셋을 통해 게임을 새로고침해주세요.")
        print(f"Just One - {datetime.datetime.now()} : <Error> {ctx.channel.id}, error: {error}")

bot.run(token)
