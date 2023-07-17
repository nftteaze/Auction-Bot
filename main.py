import os
import disnake
from disnake.ext import commands
from disnake import TextInputStyle
import sqlite3

intents = disnake.Intents.default()
intents.message_content = True

# Connect to the SQLite database
conn = sqlite3.connect('bid_data.db')
c = conn.cursor()

# Create the bid table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS bids (
                bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                product_name TEXT,
                bid_amount REAL
            )''')

conn.commit()

product_options = {
    1: "Vanta NFT",
    2: "Heist",
    3: "MadLad"
}

# Create a global dictionary to store the bids made during the /blindbid phase
phase_bids = {}

class BidModal(disnake.ui.Modal):
    def __init__(self):
        product_options_text = "\n".join(f"{key} = {value}" for key, value in product_options.items())
        product_placeholder = f"Product?\n\n{product_options_text}"

        components = [
            disnake.ui.TextInput(
                label="AD Member number",
                placeholder="Enter your member number",
                custom_id="member_number",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="How many coins would you like to bid?",
                placeholder="Enter the bid amount",
                custom_id="bid_amount",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label=product_placeholder,
                placeholder="Enter the product number",
                custom_id="product_index",
                style=TextInputStyle.short,
                max_length=2,
            )
        ]

        super().__init__(title="Asset Dash Auction", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        member_number = inter.text_values.get("member_number", "Not provided")
        bid_amount = float(inter.text_values.get("bid_amount", "0"))
        product_index = inter.text_values.get("product_index")

        if not product_index.isdigit() or int(product_index) not in product_options:
            response = "Invalid product index. Please choose a valid product index."
            await inter.response.send_message(response)
            return

        product_name = product_options[int(product_index)]
        user_id = inter.user.id
        username = inter.user.name

        # Check if the user has an existing bid for the same product
        c.execute("SELECT bid_amount FROM bids WHERE user_id = ? AND product_name = ?",
                  (user_id, product_name))
        existing_bid = c.fetchone()

        if existing_bid:
            # Update the existing bid with the new bid amount
            c.execute("UPDATE bids SET bid_amount = ? WHERE user_id = ? AND product_name = ?",
                      (bid_amount, user_id, product_name))
            conn.commit()

            response = f"Your bid for {product_name} has been updated."
            await inter.response.send_message(response)
        else:
            # Insert the new bid into the database
            c.execute("INSERT INTO bids (user_id, username, product_name, bid_amount) VALUES (?, ?, ?, ?)",
                      (user_id, username, product_name, bid_amount))
            conn.commit()

            response = f"Thanks! {inter.user.mention} your bid for {product_name} was successful."
            await inter.response.send_message(response)

            # Update phase_bids dictionary with the user's bid
            if product_name in phase_bids:
                phase_bids[product_name].append((user_id, bid_amount))
            else:
                phase_bids[product_name] = [(user_id, bid_amount)]


bot = commands.Bot(command_prefix="/", intents=intents)

def is_admin(ctx):
    admin_role_id = 1115566585382445067  # Replace with your admin role ID
    # Assuming you're using disnake.Member for the author
    return ctx.author.id == admin_role_id or any(role.id == admin_role_id for role in ctx.author.roles)

@bot.slash_command()
async def blindbid(inter: disnake.AppCmdInter):
    await inter.response.send_modal(modal=BidModal())


# Add the /phaseend command
@bot.slash_command()
@commands.check(is_admin)
async def phaseend(inter: disnake.AppCmdInter, product_name: str):
    # Check if the command is invoked within a guild context
    if inter.guild:
        # Get the successful bidders from the database
        c.execute("SELECT user_id, bid_amount FROM bids WHERE product_name = ? ORDER BY bid_amount DESC",
                  (product_name,))
        all_bids = c.fetchall()

        # Get or create the new role for the phase
        phase_role_name = f"{product_name} Phase 2"
        phase_role = disnake.utils.get(inter.guild.roles, name=phase_role_name)
        if phase_role is None:
            phase_role = await inter.guild.create_role(name=phase_role_name)

        # Assign the new role to the successful bidders
        successful_assignments = 0
        for user_id, _ in all_bids:
            member = await inter.guild.fetch_member(user_id)
            if member:
                try:
                    await member.add_roles(phase_role)
                    successful_assignments += 1
                except disnake.Forbidden:
                    pass

        # Create a new channel that only the top bidders can view
        overwrites = {
            inter.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            phase_role: disnake.PermissionOverwrite(read_messages=True),
        }
        try:
            await inter.guild.create_text_channel(f"{product_name}_Phase2", overwrites=overwrites)
        except disnake.Forbidden:
            pass

        response = f"Phase 2 for {product_name} has started."
        if successful_assignments > 0:
            response += f" Successful bidders have been given the {phase_role.name} role."

        await inter.response.send_message(response)
    else:
        await inter.response.send_message("This command is only available in a guild.")

@bot.slash_command()
async def bid(inter: disnake.AppCmdInter):
    if not inter.guild:
        await inter.response.send_message("This command is only available in a guild.")
        return

    phase_role_name = f"{inter.data['name']} Phase 2"
    phase_role = disnake.utils.get(inter.guild.roles, name=phase_role_name)

    if phase_role and phase_role in inter.author.roles:
        await inter.response.send_modal(modal=BidModal(product_input=False))
    else:
        await inter.response.send_message("You are not eligible to use this command.")

@bot.slash_command()
async def bidlist(inter: disnake.AppCmdInter, product_name: str):
    # Retrieve the bid data from the database
    c.execute("SELECT username, user_id, bid_amount FROM bids WHERE product_name = ? ORDER BY bid_amount DESC",
              (product_name,))
    bid_data = c.fetchall()

    if bid_data:
        response = f"Bid list for {product_name}:"
        for index, (username, user_id, bid_amount) in enumerate(bid_data, start=1):
            response += f"\n**{index}. <@{user_id}>**\n{username} ({user_id}) = {bid_amount}"
        await inter.response.send_message(response)
    else:
        response = f"No bids found for {product_name}."
        await inter.response.send_message(response)

@bot.slash_command()
@commands.check(is_admin)
async def bidclear(inter: disnake.AppCmdInter, product_name: str, user: disnake.User):
    # Clear bid for the specified user and product
    c.execute("DELETE FROM bids WHERE user_id = ? AND product_name = ?", (user.id, product_name))
    conn.commit()
    await inter.response.send_message(f"Bid for {product_name} by {user.mention} has been cleared.")

@bot.slash_command()
@commands.check(is_admin)
async def bidclearall(inter: disnake.AppCmdInter, product_name: str):
    # Clear all bids for the specified product
    c.execute("DELETE FROM bids WHERE product_name = ?", (product_name,))
    conn.commit()
    await inter.response.send_message(f"All bids for {product_name} have been cleared.")

# Add the /bidexport command to export the bid list to a file
@bot.slash_command()
async def bidexport(inter: disnake.AppCmdInter, product_name: str):
    c.execute("SELECT username, user_id, bid_amount FROM bids WHERE product_name = ? ORDER BY bid_amount DESC",
              (product_name,))
    bid_data = c.fetchall()

    if bid_data:
        filename = f"{product_name}_bid_list.txt"
        with open(filename, "w") as file:
            file.write(f"Bid list for {product_name}:\n")
            for index, (username, user_id, bid_amount) in enumerate(bid_data, start=1):
                file.write(f"{index}. <@{user_id}> {username} ({user_id}) = {bid_amount}\n")

        # Send the exported file as a downloadable link
        with open(filename, "rb") as file:
            await inter.response.send_message(f"Bid list for {product_name} has been exported.",
                                              file=disnake.File(file, filename))
        os.remove(filename)  # Remove the temporary file after sending
    else:
        await inter.response.send_message(f"No bids found for {product_name}.")

bot.run(os.getenv("BOT_TOKEN"))