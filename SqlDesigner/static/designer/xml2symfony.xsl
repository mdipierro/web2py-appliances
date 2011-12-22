<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/sql">
    <html>
      <body id="body">
        <xsl:variable name="newline">
          <xsl:text>
</xsl:text>
        </xsl:variable>
        <xsl:value-of select="concat('propel:', $newline)"/>
        <xsl:for-each select="table">
          <xsl:value-of select="concat('  ', @title, ':', $newline)"/>

          <xsl:for-each select="row">

            <!-- Column name -->
            <xsl:value-of select="concat('    ', title, ':')"/>

            <!-- Type information -->
            <xsl:variable name="type">
              <xsl:choose>
                <xsl:when test="type = 'Integer'">integer</xsl:when>
                <xsl:when test="type = 'Byte'">tinyint</xsl:when>
                <xsl:when test="type = 'Decimal'">decimal</xsl:when>
                <xsl:when test="type = 'Single precision'">float</xsl:when>
                <xsl:when test="type = 'Double precision'">double</xsl:when>
                <xsl:when test="type = 'Char'">char</xsl:when>
                <xsl:when test="type = 'String'">
                  <xsl:value-of select="concat('varchar(', @special, ')')"/>
                </xsl:when>
                <xsl:when test="type = 'Text'">longvarchar</xsl:when>
                <xsl:when test="type = 'Binary'">tinyint</xsl:when>
                <xsl:when test="type = 'BLOB'">blob</xsl:when>
                <xsl:when test="type = 'Date'">date</xsl:when>
                <xsl:when test="type = 'Time'">time</xsl:when>
                <xsl:when test="type = 'Datetime'">bu_date</xsl:when>
                <xsl:when test="type = 'Timestamp'">timestamp</xsl:when>
                <xsl:when test="type = 'Enum'">varchar(255)</xsl:when>
                <xsl:when test="type = 'Set'">varchar(255)</xsl:when>
              </xsl:choose>
            </xsl:variable>

            <xsl:choose>
              <xsl:when test="title='id'">
                <xsl:value-of select="$newline"/>
              </xsl:when>
              <xsl:when test="substring(title, string-length(title)-2)='_id'">
                <xsl:value-of select="$newline"/>
              </xsl:when>
              <xsl:when test="title='created_at'">
                <xsl:value-of select="$newline"/>
              </xsl:when>
              <xsl:when test="title='created_on'">
                <xsl:value-of select="$newline"/>
              </xsl:when>
              <xsl:when test="title='modified_at'">
                <xsl:value-of select="$newline"/>
              </xsl:when>
              <xsl:when test="title='modified_on'">
                <xsl:value-of select="$newline"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:text>  { </xsl:text>
                <xsl:value-of select="concat('type: ', $type)"/>
                <xsl:if test="@nn">
                  <xsl:text>, required: true</xsl:text>
                </xsl:if>
                <xsl:choose>
                  <xsl:when test="@pk">
                    <xsl:text>, primaryKey: true</xsl:text>
                    <xsl:if test="$type='integer'">
                      <xsl:text>, autoincrement: true</xsl:text>
                    </xsl:if>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:if test="string-length(default)>0">
                      <xsl:value-of select="concat(', default: ', default)"/>
                    </xsl:if>
                  </xsl:otherwise>
                </xsl:choose>
                <xsl:value-of select="concat(' }', $newline)"/>
              </xsl:otherwise>
            </xsl:choose>

          </xsl:for-each>

        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
