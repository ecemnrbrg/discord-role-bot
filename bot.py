import discord
from discord.ext import commands

ALLOWED_USERS = [631492725878947862, 288714000831610880]


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

roles_data = {}
roles_message = None


class RoleModal(discord.ui.Modal, title="Rol Listesi"):
    roles_input = discord.ui.TextInput(
        label="Roller (her satıra bir rol)",
        style=discord.TextStyle.paragraph,
        placeholder="healer\nduelist\ntank",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        global roles_data, roles_message

        roles_data = {}

        lines = self.roles_input.value.split("\n")

        counter = 1
        for role in lines:
            role = role.strip()
            if role == "":
                continue

            roles_data[str(counter)] = {"name": role, "user": None}
            counter += 1

        text = ""
        for num, data in roles_data.items():
            text += f"{num} - {data['name']}\n"

        roles_message = await interaction.channel.send(text)
        await interaction.response.send_message(
            "Roller oluşturuldu!", ephemeral=True
        )


@bot.tree.command(name="roller", description="Rol listesi oluştur")
async def roller(interaction: discord.Interaction):

    if interaction.user.id not in ALLOWED_USERS:
        await interaction.response.send_message(
            "Bu komutu kullanamazsın.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(RoleModal())



@bot.event
async def on_message(message):
    global roles_data, roles_message

    if message.author.bot:
        return

    content = message.content.strip()

    # Role girme
    if content in roles_data:
        choice = content

        # rol doluysa değiştirme
        if roles_data[choice]["user"] is not None:
            return

        # eski rolü temizle
        for r in roles_data:
            if roles_data[r]["user"] == message.author:
                roles_data[r]["user"] = None

        roles_data[choice]["user"] = message.author

    # Rolden çıkma
    elif content.startswith("-"):
        num = content[1:]

        if num in roles_data and roles_data[num]["user"] == message.author:
            roles_data[num]["user"] = None
        else:
            return

    else:
        await bot.process_commands(message)
        return

    text = ""
    for num, data in roles_data.items():
        if data["user"]:
            text += f"{num} - {data['name']} {data['user'].mention}\n"
        else:
            text += f"{num} - {data['name']}\n"

    if roles_message:
        await roles_message.edit(content=text)

    await bot.process_commands(message)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot hazır!")


import os
bot.run(os.getenv("TOKEN"))


