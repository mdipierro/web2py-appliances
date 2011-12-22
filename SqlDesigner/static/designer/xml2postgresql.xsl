<xsl:stylesheet version = '1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<xsl:template match="/sql">
		<html>
		<body id="body">
		<xsl:for-each select="table">
			<xsl:text>CREATE TABLE </xsl:text>
			<xsl:value-of select="@title" />
			<xsl:text>(
</xsl:text>
			<xsl:for-each select="row">
				<xsl:text></xsl:text>
				<xsl:value-of select="title" />
				<xsl:text> </xsl:text>

				<xsl:if test="type = 'Integer'">
					<xsl:text>INTEGER</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Byte'">
					<xsl:text>BIT</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Decimal'">
					<xsl:text>decimal</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Single precision'">
					<xsl:text>FLOAT</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Double precision'">
					<xsl:text>DOUBLE</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'Char'">
					<xsl:text>char</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'String'">
					<xsl:text>character varying</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>) </xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Text'">
					<xsl:text>text</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Binary'">
					<xsl:text>bytea</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>) </xsl:text>
				</xsl:if>

				<xsl:if test="type = 'BLOB'">
					<xsl:text>oid</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Date'">
					<xsl:text>DATE</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Time'">
					<xsl:text>TIME</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Datetime'">
					<xsl:text>timestamp</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Timestamp'">
					<xsl:text>TIMESTAMP</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Enum'">
					<xsl:text>[sql_variant]</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>) </xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Set'">
					<xsl:text>[sql_variant]</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>) </xsl:text>
				</xsl:if>

				<xsl:text> </xsl:text>

				<xsl:if test="@nn">
					<xsl:text>NOT NULL </xsl:text>
				</xsl:if>

				<xsl:choose>
					<xsl:when test="@pk">
						<xsl:text>serial</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text>default '</xsl:text>
						<xsl:value-of select="default" />
						<xsl:text>'</xsl:text>
					</xsl:otherwise>
				</xsl:choose>

				<xsl:if test="not (position()=last())">
					<xsl:text>,
</xsl:text>
				</xsl:if>
			</xsl:for-each>

			<xsl:for-each select="row">
				<xsl:choose>
					<xsl:when test="@pk">
						<xsl:text>,
</xsl:text>
						<xsl:text>PRIMARY KEY (</xsl:text>
						<xsl:value-of select="title" />
						<xsl:text>)</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:if test="@index">
							<xsl:text>,
</xsl:text>
							<xsl:text>KEY </xsl:text>
							<xsl:value-of select="title" />
							<xsl:text> (</xsl:text>
							<xsl:value-of select="title" />
							<xsl:text>)</xsl:text>
						</xsl:if>
					</xsl:otherwise>
				</xsl:choose>

			</xsl:for-each>
			<xsl:text>
);

</xsl:text>
		</xsl:for-each>
		</body>
		</html>
	</xsl:template>

</xsl:stylesheet>