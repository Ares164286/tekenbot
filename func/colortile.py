import discord
from discord.ext import commands
from discord import ui
import random

GRID_WIDTH = 5  # 表示範囲を小さく設定
GRID_HEIGHT = 5
TOTAL_TILES = 20
COLORS = ["🔴", "🟢", "🔵", "🟡", "🟣"]

class TileButton(ui.Button):
    def __init__(self, row, col, color, game_instance):
        super().__init__(style=discord.ButtonStyle.secondary, label="", row=row)
        self.row = row
        self.col = col
        self.color = color
        self.game_instance = game_instance
        self.emoji = color

    async def callback(self, interaction: discord.Interaction):
        """タイルが選択されたときの処理"""
        await self.game_instance.select_tile(interaction, self.row, self.col)

class ColorTileGameView(ui.View):
    def __init__(self, game_instance):
        super().__init__(timeout=None)  # タイムアウトなし
        self.game_instance = game_instance
        self.update_board()

    def update_board(self):
        """現在の盤面の状態に基づいてボタンを更新"""
        self.clear_items()  # 既存のボタンをクリア
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                color = self.game_instance.grid[row][col]
                button = TileButton(row, col, color, self.game_instance)
                self.add_item(button)

class DiscordColorTileGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_active = False

    @commands.command(name="start_colortile")
    async def start_game(self, ctx):
        """Discord上でカラータイルのゲームを開始"""
        if self.game_active:
            await ctx.send("既にゲームが進行中です。")
            return

        # ゲームの初期化
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.place_initial_tiles()
        self.score = 0
        self.game_active = True

        await ctx.send("カラータイルのゲームを開始します！")

        # 盤面を表示
        self.view = ColorTileGameView(self)
        await ctx.send(f"スコア: {self.score}", view=self.view)

    def place_initial_tiles(self):
        """初期タイルのランダム配置"""
        positions = random.sample([(row, col) for row in range(GRID_HEIGHT) for col in range(GRID_WIDTH)], TOTAL_TILES)
        for (row, col) in positions:
            self.grid[row][col] = random.choice(COLORS)

    async def select_tile(self, interaction, row, col):
        """タイルを選択し、色を変更する処理"""
        if not self.game_active:
            await interaction.response.send_message("ゲームが開始されていません。`!start_colortile`で開始してください。", ephemeral=True)
            return

        color_to_clear = self.grid[row][col]
        if color_to_clear:
            removed_tiles = self.clear_adjacent_tiles(row, col, color_to_clear)
            self.score += removed_tiles

            # 盤面を更新
            self.view.update_board()
            await interaction.response.edit_message(content=f"スコア: {self.score}", view=self.view)

            # ゲームクリアの確認
            if all(tile == self.grid[0][0] for row in self.grid for tile in row if tile):
                self.game_active = False
                await interaction.followup.send("おめでとうございます！全てのタイルが同じ色になりました！")

    def clear_adjacent_tiles(self, row, col, color):
        """隣接する同じ色のタイルを消去"""
        cleared_count = 0
        if self.grid[row][col] == color:
            self.grid[row][col] = None  # タイルを削除
            cleared_count += 1
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, c = row + dr, col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH and self.grid[r][c] == color:
                    cleared_count += self.clear_adjacent_tiles(r, c, color)
        return cleared_count

    @commands.command(name="reset_colortile")
    async def reset_game(self, ctx):
        """ゲームをリセット"""
        self.game_active = False
        await ctx.send("ゲームがリセットされました。新しいゲームを開始できます。")

async def setup(bot):
    await bot.add_cog(DiscordColorTileGame(bot))
