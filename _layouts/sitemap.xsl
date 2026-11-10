<?xml version="1.0" encoding="UTF-8"?>
<!-- Human-readable view of sitemap.xml and sitemap_index.xml. Search engines ignore it. -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>
<xsl:template match="/">
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="robots" content="noindex"/>
<title>Sitemap · {{ site.title }}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&amp;family=IBM+Plex+Sans:wght@400;500;600&amp;display=swap"/>
<style>
*{box-sizing:border-box}
body{margin:0;background:#101112;color:#eceae4;font:400 15px/1.6 'IBM Plex Sans','Segoe UI',Helvetica,Arial,sans-serif}
a{color:#eceae4;text-decoration:none}a:hover{color:#ff7700}
.wrap{max-width:1000px;margin:0 auto;padding:40px 16px 64px}
.eyebrow{font:600 11px/1.3 'IBM Plex Mono',Menlo,Consolas,monospace;letter-spacing:2px;color:#ff6c15}
h1{margin:8px 0 8px;font-size:32px;line-height:1.15;font-weight:600;letter-spacing:-.02em}
p{margin:0 0 24px;color:#a3a29e;max-width:60ch}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1px;background:#3a3a3c;border:1px solid #3a3a3c;border-radius:4px;overflow:hidden;margin-bottom:24px}
.stats div{background:#101112;padding:10px 12px}
.stats span{display:block;font:400 11px/1.5 Tahoma,'Segoe UI',sans-serif;color:#a3a29e}
.stats b{font:400 15px/1.4 'IBM Plex Mono',Menlo,Consolas,monospace}
.scroll{overflow-x:auto;border:1px solid #232324;border-radius:8px;background:#151617}
table{width:100%;border-collapse:collapse;min-width:520px}
th{text-align:left;padding:10px 14px;font:400 11px/1.5 Tahoma,'Segoe UI',sans-serif;color:#a3a29e;border-bottom:1px solid #3a3a3c}
td{padding:12px 14px;border-bottom:1px solid #232324;font-size:14px;word-break:break-all}
tr:last-child td{border-bottom:0}
td.n,td.d{font:400 13px/1.5 'IBM Plex Mono',Menlo,Consolas,monospace;color:#a3a29e;white-space:nowrap;word-break:normal}
.foot{margin-top:24px;font-size:12px;color:#8e8d88}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">SITEMAP</div>
  <xsl:choose>
    <xsl:when test="s:sitemapindex">
      <h1>{{ site.title }}: sitemap index</h1>
      <p>This index lists the sitemap files of the help center. Open one to see its pages.</p>
      <div class="stats"><div><span>Sitemap files</span><b><xsl:value-of select="count(s:sitemapindex/s:sitemap)"/></b></div></div>
      <div class="scroll"><table>
        <thead><tr><th>#</th><th>Sitemap</th><th>Last modified</th></tr></thead>
        <tbody>
        <xsl:for-each select="s:sitemapindex/s:sitemap">
          <tr>
            <td class="n"><xsl:value-of select="position()"/></td>
            <td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td>
            <td class="d"><xsl:value-of select="substring(s:lastmod,1,10)"/></td>
          </tr>
        </xsl:for-each>
        </tbody>
      </table></div>
    </xsl:when>
    <xsl:otherwise>
      <h1>{{ site.title }}: pages</h1>
      <p>Every public page in this sitemap, as search engines see it.</p>
      <div class="stats"><div><span>Pages</span><b><xsl:value-of select="count(s:urlset/s:url)"/></b></div></div>
      <div class="scroll"><table>
        <thead><tr><th>#</th><th>Address</th><th>Last modified</th></tr></thead>
        <tbody>
        <xsl:for-each select="s:urlset/s:url">
          <tr>
            <td class="n"><xsl:value-of select="position()"/></td>
            <td><a href="{s:loc}"><xsl:value-of select="s:loc"/></a></td>
            <td class="d"><xsl:value-of select="substring(s:lastmod,1,10)"/></td>
          </tr>
        </xsl:for-each>
        </tbody>
      </table></div>
    </xsl:otherwise>
  </xsl:choose>
  <div class="foot"><a href="{{ url('/sitemap_index.xml') }}">Sitemap index</a> · <a href="{{ url('/sitemap.xml') }}">All pages</a> · <a href="{{ url('/') }}">Help home</a></div>
</div>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
