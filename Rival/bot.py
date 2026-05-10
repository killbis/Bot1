import discord
from discord import guild
from discord.ext import commands

TOKEN = 'MTUwMjkyODA4Njc1OTUwNjAyMQ.GrZWe4.EFK69Y52SAbYMBL1r4iK9n7G5G7TopwlFBaJhI'
APPLICATION_CHANNEL_ID = 1502953276000305247
APPLICATION_LOG_CHANNEL_ID = 1502953276000305243
APPLICATION_RESULT_CHANNEL_ID = 1502955015201886300

OBZVON_ROLE_ID = 1502954282377543680
NEW_ROLE_ID = 1502953275547324500

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

invite_cache = {}

class ReviewApplicationView(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(
        label='Обзвон',
        style=discord.ButtonStyle.secondary,
        custom_id='obzvon'
    )
    async def obzvon_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        if guild is None:
            return

        member = guild.get_member(self.applicant_id)

        if member is None:
            await interaction.response.send_message(
                'Участник не найден.',
                ephemeral=True
            )
            return

        role = guild.get_role(OBZVON_ROLE_ID)

        if role is None:
            await interaction.response.send_message(
                'Роль обзвона не найдена.',
                ephemeral=True
            )
            return

        try:
            await member.add_roles(role)

        except discord.Forbidden:
            await interaction.response.send_message(
                'У бота нет прав на выдачу роли.',
                ephemeral=True
            )
            return

        try:
            await member.send(
                '📞 Вас пригласили на обзвон.\n'
                'Ожидайте дальнейшей информации.\n'
                'Канал: <#1502953276205961317>'
            )

        except:
            pass

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.orange()

        embed.add_field(
            name='Обзвон',
            value=f'📞 На обзвоне — {interaction.user.mention}',
            inline=False
        )

        await interaction.message.edit(
            embed=embed,
            view=ObzvonResultView(self.applicant_id)
        )

        await interaction.response.send_message(
            'Игрок отправлен на обзвон.',
            ephemeral=True
        )


class ObzvonResultView(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(
        label='Одобрено',
        style=discord.ButtonStyle.success,
        custom_id='obzvon_pass'
    )
    async def passed_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        if guild is None:
            return

        member = guild.get_member(self.applicant_id)

        if member is None:
            return

        role = guild.get_role(NEW_ROLE_ID)

        if role is None:
            await interaction.response.send_message(
                'Роль не найдена.',
                ephemeral=True
            )
            return

        await member.add_roles(role)

        embed = interaction.message.embeds[0]

        embed.color = discord.Color.green()

        embed.add_field(
            name='Результат обзвона',
            value=f'✅ Одобрено — {interaction.user.mention}',
            inline=False
        )

        await interaction.message.edit(
            embed=embed,
            view=None
        )

        result_channel = guild.get_channel(
            APPLICATION_RESULT_CHANNEL_ID
        )

        if result_channel:
            await result_channel.send(
                f'✅ {member.mention} прошел обзвон '
                f'и получил роль {role.mention}'
            )

        try:
            await member.send(
                '✅ Вы успешно прошли обзвон.'
            )

        except:
            pass

        await interaction.response.send_message(
            'Игрок одобрен.',
            ephemeral=True
        )

    @discord.ui.button(
        label='Не одобрено',
        style=discord.ButtonStyle.danger,
        custom_id='obzvon_fail'
    )
    async def failed_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            ObzvonFailModal(
                self.applicant_id,
                interaction.message.id,
                interaction.channel.id
            )
        )


class ObzvonFailModal(discord.ui.Modal, title='Причина отказа'):

    reason = discord.ui.TextInput(
        label='Причина отказа',
        style=discord.TextStyle.long,
        placeholder='Введите причину отказа',
        required=True,
        max_length=400
    )

    def __init__(
        self,
        applicant_id: int,
        message_id: int,
        channel_id: int
    ):
        super().__init__()

        self.applicant_id = applicant_id
        self.message_id = message_id
        self.channel_id = channel_id

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        if guild is None:
            return

        member = guild.get_member(self.applicant_id)

        channel = guild.get_channel(self.channel_id)

        if member is None or channel is None:
            return

        try:
            message = await channel.fetch_message(
                self.message_id
            )

        except:
            return

        embed = message.embeds[0]

        embed.color = discord.Color.red()

        embed.add_field(
            name='Результат обзвона',
            value=f'❌ Не одобрено — {interaction.user.mention}',
            inline=False
        )

        embed.add_field(
            name='Причина',
            value=self.reason.value,
            inline=False
        )

        await message.edit(
            embed=embed,
            view=None
        )

        result_channel = guild.get_channel(
            APPLICATION_RESULT_CHANNEL_ID
        )

        if result_channel:
            await result_channel.send(
                f'❌ {member.mention} не прошел обзвон.\n'
                f'Причина: {self.reason.value}'
            )

        try:
            await member.send(
                f'❌ Вы не прошли обзвон.\n'
                f'Причина: {self.reason.value}'
            )

        except:
            pass

        await interaction.response.send_message(
            'Отказ отправлен.',
            ephemeral=True
        )


class ApplicationModal(discord.ui.Modal, title='Подача заявки'):
    name_age = discord.ui.TextInput(
        label='Имя, возраст (OOC) *',
        style=discord.TextStyle.short,
        placeholder='Например: Иван, 18',
        required=True,
    )
    time_on_server = discord.ui.TextInput(
        label='Время на маджестике *',
        style=discord.TextStyle.short,
        required=True,
    )
    other_fams = discord.ui.TextInput(
        label='Были в других семьях?',
        style=discord.TextStyle.long,
        required=False,
    )
    hours_per_day = discord.ui.TextInput(
        label='Часов в день играете? *',
        style=discord.TextStyle.short,
        required=True,
    )

    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message('Ошибка: не удалось определить сервер.', ephemeral=True)
            return

        log_channel = guild.get_channel(APPLICATION_LOG_CHANNEL_ID)
        if log_channel is None:
            log_channel = discord.utils.get(guild.text_channels, name='application-logs')
        if log_channel is None:
            log_channel = guild.system_channel or (guild.text_channels[0] if guild.text_channels else None)

        description = (
            f'**Имя, возраст (OOC):** {self.name_age.value}\n'
            f'**Время на маджестике:** {self.time_on_server.value}\n'
            f'**Другие семьи:** {self.other_fams.value or "-"}\n'
            f'**Часов в день:** {self.hours_per_day.value}'
        )

        embed = discord.Embed(
            title='Новая заявка в семью',
            description=description,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f'ID: {interaction.user.id}')

        if log_channel is not None:
            view = ReviewApplicationView(interaction.user.id)
            await log_channel.send(content=f'Заявка от {interaction.user.mention}', embed=embed, view=view)

        await interaction.response.send_message('Заявка отправлена! Ожидайте ответа.', ephemeral=True)

class ApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Подать заявку в семью!', style=discord.ButtonStyle.primary, custom_id='apply_family_button')
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApplicationModal(interaction.user))

async def ensure_application_message(guild: discord.Guild):
    form_channel = guild.get_channel(APPLICATION_CHANNEL_ID)
    if not isinstance(form_channel, discord.TextChannel):
        return

    async for message in form_channel.history(limit=50):
        if message.author == bot.user and message.components:
            for row in message.components:
                for component in getattr(row, 'children', []):
                    if getattr(component, 'custom_id', None) == 'apply_family_button':
                        return

    embed = discord.Embed(
        title='📋 Заявки в семью Rival',
        description='Нажмите на кнопку ниже, чтобы подать заявку',
        color=discord.Color.blue()
    )
    embed.set_image(url='https://i.imgur.com/S6CL4LH.png')
    embed.add_field(
        name='ℹ️ Информация',
        value='✅ Вы будете уведомлены о принятии или отклонении заявки\n⏱️ Время рассмотрения заявки до 2 дней',
        inline=False
    )
    
    await form_channel.send(embed=embed, view=ApplyView())

async def cache_guild_invites(guild: discord.Guild):
    invites = await guild.invites()
    invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}

@bot.event
async def on_ready():
    bot.add_view(ApplyView())
    for guild in bot.guilds:
        await cache_guild_invites(guild)
        await ensure_application_message(guild)
    print(f'Logged in as {bot.user}')

@bot.event
async def on_guild_join(guild: discord.Guild):
    await cache_guild_invites(guild)
    await ensure_application_message(guild)

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    before_invites = invite_cache.get(guild.id, {})
    invites = await guild.invites()
    joined_invite = None

    for invite in invites:
        previous_uses = before_invites.get(invite.code, 0)
        if invite.uses > previous_uses:
            joined_invite = invite
            break

    await cache_guild_invites(guild)

    log_channel = discord.utils.get(guild.text_channels, name='invite-logs')
    if log_channel is None:
        log_channel = guild.system_channel or (guild.text_channels[0] if guild.text_channels else None)

    if log_channel is not None:
        if joined_invite is not None:
            await log_channel.send(
                f'✅ {member.mention} joined using invite `{joined_invite.code}` created by {joined_invite.inviter}. '
                f'Uses: {joined_invite.uses}/{joined_invite.max_uses or "∞"}'
            )
        else:
            await log_channel.send(f'⚠️ {member.mention} joined, но пригласившего не удалось определить.')

@bot.command(name='create_invite')
@commands.has_guild_permissions(create_instant_invite=True)
async def create_invite(ctx: commands.Context, max_age: int = 0, max_uses: int = 0):
    invite = await ctx.channel.create_invite(max_age=max_age, max_uses=max_uses, unique=True)
    await ctx.send(
        f"Создан invite: {invite.url}\nМакс. использование: {invite.max_uses or '∞'}\nСрок действия: {invite.max_age or 'не ограничен'} сек."
    )

@bot.command(name='invites')
async def invites(ctx: commands.Context):
    invites = await ctx.guild.invites()
    if not invites:
        return await ctx.send('В этом сервере нет активных приглашений.')

    lines = [
        f'`{invite.code}` | создал {invite.inviter} | использовано {invite.uses}/{invite.max_uses or "∞"}'
        for invite in invites
    ]
    await ctx.send('\n'.join(lines[:10]))

@bot.command(name='post_form')
@commands.has_guild_permissions(manage_guild=True)
async def post_form(ctx: commands.Context):
    await ensure_application_message(ctx.guild)
    await ctx.send('Форма заявки теперь есть в канале.')

bot.run(TOKEN)
