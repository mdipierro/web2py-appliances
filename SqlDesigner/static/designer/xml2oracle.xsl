<!--
	XML 2 Oracle XSL transformation for WWW SQL Designer
	Version: 0.1 Beta
	Author: rfevre@falco.fr
-->

<xsl:stylesheet version = '1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<xsl:template match="/sql">
		<html>
		<body id="body">
		<xsl:for-each select="table">
			<xsl:text>CREATE TABLE "</xsl:text>
			<xsl:value-of select="@title" />
			<xsl:variable name="table" select="@title"/>
			<xsl:text>" (</xsl:text>
			<xsl:for-each select="row">
				<xsl:text>"</xsl:text>
				<xsl:value-of select="title" />
				<xsl:text>" </xsl:text>

				<xsl:if test="type = 'Integer'">
					<xsl:text>number(10)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Byte'">
					<xsl:text>number(1)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Decimal'">
					<xsl:text>decimal</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'Single precision'">
					<xsl:text>float(10)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Double precision'">
					<xsl:text>float(12)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Char'">
					<xsl:text>char</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'String'">
					<xsl:text>varchar2</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Text'">
					<xsl:text>long</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Binary'">
					<xsl:text>bfile</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'BLOB'">
					<xsl:text>blob</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Date'">
					<xsl:text>date</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Time'">
					<xsl:text>date</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Datetime'">
					<xsl:text>date</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Timestamp'">
					<xsl:text>[timestamp]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Enum'">
					
				</xsl:if>

				<xsl:if test="type = 'Set'">
				
				</xsl:if>

				<xsl:text> </xsl:text>

				<xsl:if test="@pk">
					<!-- La clef auto -->
					<!-- <xsl:text>IDENTITY (1, 1) NOT </xsl:text> -->
				</xsl:if>

				<xsl:if test="@nn">
					<xsl:text>NOT </xsl:text>
				</xsl:if>

				<xsl:text>NULL </xsl:text>

				<xsl:if test="@pk">
					<xsl:text>CONSTRAINT PK_</xsl:text>
					<xsl:value-of select="$table" />
					<xsl:text>_</xsl:text>
					<xsl:value-of select="title" />
					<xsl:text> PRIMARY KEY </xsl:text>
				</xsl:if>
				
				<xsl:if test="not (position()=last())">
					<xsl:text>,
</xsl:text>
				</xsl:if>
			</xsl:for-each>

			<xsl:text>
);

</xsl:text>
		</xsl:for-each>
		<xsl:for-each select="relation">
			<!-- begin variable -->
			<xsl:variable name="table_PK" select="table_1"/>
			<xsl:variable name="table_FK" select="table_2"/>
			<xsl:variable name="row_PK" select="row_1"/>
			<xsl:variable name="row_FK" select="row_2"/>
			<!-- end variable -->
			<xsl:text>ALTER TABLE "</xsl:text>
			<xsl:for-each select="../table[@id=$table_FK]">
				<xsl:value-of select="@title" />
			</xsl:for-each>
			<xsl:text>" ADD (CONSTRAINT FK_</xsl:text>
			<xsl:for-each select="../table[@id=$table_FK]">
				<xsl:value-of select="@title" />
			</xsl:for-each>
			<xsl:text>_</xsl:text>
			<xsl:for-each select="../table[@id=$table_FK]/row[@id=$row_FK]">
				<xsl:value-of select="title" />
			</xsl:for-each>
			<xsl:text> FOREIGN KEY ("</xsl:text>
			<xsl:for-each select="../table[@id=$table_FK]/row[@id=$row_FK]">
				<xsl:value-of select="title" />
			</xsl:for-each>
			<xsl:text>") REFERENCES "</xsl:text>
			<xsl:for-each select="../table[@id=$table_PK]">
				<xsl:value-of select="@title" />
			</xsl:for-each>
			<xsl:text>"("</xsl:text>
			<xsl:for-each select="../table[@id=$table_PK]/row[@id=$row_PK]">
				<xsl:value-of select="title" />
			</xsl:for-each>
			<xsl:text>"));

</xsl:text>
		</xsl:for-each>
		<xsl:text>
</xsl:text>
		</body>
		</html>
	</xsl:template>

</xsl:stylesheet>