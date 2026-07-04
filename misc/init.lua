local gh = "https://github.com/"
local plugins = {
    gh .. "nvim-treesitter/nvim-treesitter",   -- formatting and syntax highlighting
    gh .. "lewis6991/ts-install.nvim",         -- auto install missing parsers
    gh .. "neovim/nvim-lspconfig",             -- default lsp configs
    gh .. "williamboman/mason.nvim",           -- lsp/debug/linter/formatter package manager library
    gh .. "williamboman/mason-lspconfig.nvim", -- lsp config bridge
    gh .. "chomosuke/typst-preview.nvim",      -- live typst preview
    gh .. "ibhagwan/fzf-lua",                  -- fuzzy file finder
    gh .. "saghen/blink.lib",                  -- blink dependency
    gh .. "saghen/blink.cmp",                  -- completion engine
    gh .. "mofiqul/vscode.nvim",               -- colorscheme
}
vim.pack.add(plugins, { confirm = false })

local lsp_servers = {
    lua_ls = {
        Lua = {
            diagnostics = {
                globals = { "vim" },
            },
            workspace = {
                library = vim.api.nvim_get_runtime_file("lua", true)
            },
        },
    },
    pylsp = {},
    tinymist = {},
}

for server, config in pairs(lsp_servers) do
    vim.lsp.config(server, {
        settings = config
    })
end

require("ts-install").setup({
    auto_install = true,
})

require("mason").setup()
require("mason-lspconfig").setup({
    ensure_installed = vim.tbl_keys(lsp_servers),
})

require("fzf-lua").setup({
    actions = {
        files = {
            ["enter"]  = FzfLua.actions.file_tabedit,
            ["ctrl-s"] = FzfLua.actions.file_split,
            ["ctrl-v"] = FzfLua.actions.file_vsplit,
            ["ctrl-t"] = FzfLua.actions.file_tabedit,
        }
    }
})

require("typst-preview").setup({
    port = 3000,
    host = "192.168.50.5",
})

require("blink.cmp").build():wait(60000)
require("blink.cmp").setup({
    cmdline = {
        completion = { menu = { auto_show = true } },
    },
    completion = {
        menu = {
            draw = {
                columns = { { 'label', 'label_description' } },
            }
        }
    },
    signature = { enabled = true },
})

vim.diagnostic.config({ virtual_text = true })

vim.g.mapleader = " "
vim.g.maplocalleader = " "

vim.api.nvim_create_autocmd('FileType', {
    pattern = { 'css', 'lua', 'html', 'json' },
    callback = function()
        vim.treesitter.start()
    end
})

vim.api.nvim_create_autocmd('FileType', {
    pattern = 'python',
    callback = function(ev)
        vim.treesitter.start()
        vim.cmd.colorscheme("vscode")
    end
})

vim.keymap.set("n", "<Esc>", "<Cmd>noh<CR>")
vim.keymap.set("n", "<leader>cd", "<Cmd>colorscheme default<CR>")
vim.keymap.set("n", "<leader>cv", "<Cmd>colorscheme vscode<CR>")
vim.keymap.set("n", "<leader>ff", "<Cmd>lua vim.lsp.buf.format({})<CR>")
vim.keymap.set("n", "<leader>fs", "<Cmd>FzfLua files cwd=~/<CR>")
vim.keymap.set("n", "<leader>gs", "<Cmd>FzfLua grep cwd=~/<CR>")
vim.keymap.set("n", "<leader>tt", "<Cmd>TypstPreviewToggle<CR>")

vim.keymap.set("n", "<leader>pp", "<Cmd>lua vim.pack.update(nil, { offline = true })<CR>")
vim.keymap.set("n", "<leader>pu", "<Cmd>lua vim.pack.update()<CR>")

vim.opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
-- vim.opt.foldenable = true
-- vim.opt.foldlevel = 99
vim.opt.foldmethod = "indent"
vim.opt.foldlevelstart = 99

vim.opt.cursorline = true
vim.opt.expandtab = true
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.shiftwidth = 4
vim.opt.signcolumn = "yes"
vim.opt.smarttab = false
vim.opt.termguicolors = true
vim.opt.undofile = true
vim.opt.wrap = false
