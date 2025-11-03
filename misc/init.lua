local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
    local lazyrepo = "https://github.com/folke/lazy.nvim.git"
    local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
    if vim.v.shell_error ~= 0 then
	vim.api.nvim_echo({
	    { "Failed to clone lazy.nvim:\n", "ErrorMsg" },
	    { out,                            "WarningMsg" },
	    { "\nPress any key to exit..." },
	}, true, {})
	vim.fn.getchar()
	os.exit(1)
    end
end
vim.opt.rtp:prepend(lazypath)

vim.g.loaded_node_provider = 0
vim.g.loaded_perl_provider = 0
vim.g.loaded_ruby_provider = 0
vim.g.mapleader = " "
vim.g.maplocalleader = "\\"
vim.g.python3_host_prog = "/usr/bin/python3"

vim.opt.backup = false
vim.opt.expandtab = true
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.shiftwidth = 4
vim.opt.signcolumn = "yes"
--vim.opt.smarttab = false --<bs> deletes spaces and not tabs
vim.opt.termguicolors = true
vim.opt.undofile = true
vim.opt.undolevels = 10000
vim.opt.updatetime = 400
vim.opt.wrap = false

require("lazy").setup({
    spec = {
	{ "Mofiqul/vscode.nvim", opts = {} },
	{
	    "nvim-neo-tree/neo-tree.nvim",
	    branch = "v3.x",
	    dependencies = {
		"nvim-lua/plenary.nvim",
		"nvim-tree/nvim-web-devicons",
		"MunifTanjim/nui.nvim",
	    },
	    opts = {
		default_component_configs = {
		    icon = {
			folder_closed = "📁",
			folder_open = "📂",
			folder_empty = "🗀",
			folder_empty_open = "🗁",
		    }
		}
	    },
	},
	{
	    "nvim-treesitter/nvim-treesitter",
	    build = ":TSUpdate",
	    config = function()
		local configs = require("nvim-treesitter.configs")
		configs.setup({
		    ensure_installed = { "c", "lua", "markdown", "vim", "vimdoc", "query", "python", "javascript", "html" },
		    sync_install = false,
		    highlight = { enable = true },
		    indent = { enable = true },
		})
	    end
	},
	{
	    'saghen/blink.cmp',
	    version = '*',
	    opts = {
		keymap = { preset = 'default' ,
		    ["<c-u>"] = { "scroll_documentation_up" },
		    ["<c-d>"] = { "scroll_documentation_down" },
		},
		-- completion = {
		--     ghost_text = { enabled = true },
		-- },
		signature = { enabled = true },

		--appearance start
		appearance = {
		    use_nvim_cmp_as_default = true,
		    nerd_font_variant = nil,
		    kind_icons = {
			Text = "",
			Method = "",
			Function = "",
			Constructor = "",

			Field = "",
			Variable = "",
			Property = "",

			Class = "",
			Interface = "",
			Struct = "",
			Module = "",

			Unit = "",
			Value = "",
			Enum = "",
			EnumMember = "",

			Keyword = "",
			Constant = "",

			Snippet = "",
			Color = "",
			File = "",
			Reference = "",
			Folder = "",
			Event = "",
			Operator = "",
			TypeParameter = "",
		    }
		},
		--appearance end
	    },
	},
	{
	    "williamboman/mason.nvim",
	    opts = {
		ui = {
		    icons = {
			package_installed = "✓",
			package_pending = "➜",
			package_uninstalled = "✗"
		    }
		}
	    }
	},
	{
	    "williamboman/mason-lspconfig.nvim",
	    opts = {
		ensure_installed = { "lua_ls", "pylsp" }
	    },
	},
	{
	    "neovim/nvim-lspconfig",
            dependencies = { "saghen/blink.cmp" },
            config = function()
                local capabilities = require("blink.cmp").get_lsp_capabilities()
                -- local lspconfig = require("lspconfig")
                -- lspconfig['pylsp'].setup({
                vim.lsp.config({"pylsp", {
                    capabilities = capabilities,
                    settings = {
                        pylsp = {
                            plugins = {
                                autopep8 = { enabled = false },
                                flake8 = { enabled = false },
                                mccabe = { enabled = false },
                                pycodestyle = { enabled = false },
                                pydocstyle = { enabled = false },
                                pyflakes = { enabled = false },
                                pylint = { enabled = false },
                                yapf = { enabled = false },
                            }
                        }
                    }
                })
                -- lspconfig['lua_ls'].setup({
                vim.lsp.config({"lua_ls", {
                    capabilities = capabilities,
                    settings = {
                        Lua = {
                            diagnostics = {
                                globals = { "vim" }
                            }
                        }
                    }
                })
                -- lspconfig['ruff'].setup({
                vim.lsp.config({"ruff", {
                    capabilities = capabilities
                })
            end,
        },
    },
    install = { colorscheme = { "habamax" } },
    checker = { enabled = true },
    ui = {
        icons = {
            cmd = "⌘",
            config = "🛠",
            event = "📅",
            ft = "📂",
            init = "⚙",
            keys = "🗝",
            plugin = "🔌",
            runtime = "💻",
            require = "🌙",
            source = "📄",
            start = "🚀",
            task = "📌",
            lazy = "💤 ",
        },
    },
})

vim.keymap.set("n", "<Esc>", "<Cmd>noh<CR>")
vim.keymap.set("n", "<C-n>", "<Cmd>Neotree toggle<CR>")
vim.keymap.set("n", "<leader>rr", "<Cmd>lua vim.lsp.buf.definition({})<CR>")
vim.keymap.set("n", "<leader>ff", "<Cmd>lua vim.lsp.buf.format({})<CR>")
vim.cmd.colorscheme("vscode")
