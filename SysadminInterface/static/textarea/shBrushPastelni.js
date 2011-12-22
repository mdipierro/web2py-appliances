dp.sh.Brushes.PasteIni = function()
{

	this.regexList = [
		{ regex: new RegExp('^#.*', 'gm'),						css: 'comment' },
    { regex: new RegExp('^\\[.*\\]$', 'gm'),						css: 'header' },
    { regex: new RegExp('^use\ =\ (\\w|:)*', 'gm'),						css: 'use' },
		{ regex: new RegExp('\%\\(\\w+\\)s', 'gm'),						css: 'interp-variable' },
		{ regex: new RegExp('\\${\\w+}', 'gm'),						css: 'variable' }
		];

	this.CssClass = 'dp-paste-ini';
}

dp.sh.Brushes.PasteIni.prototype	= new dp.sh.Highlighter();
dp.sh.Brushes.PasteIni.Aliases	= ['pasteini'];
