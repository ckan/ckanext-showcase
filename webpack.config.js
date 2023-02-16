// webpack.config.js

'use strict';

const path = require( 'path' );
const { styles } = require( '@ckeditor/ckeditor5-dev-utils' );
const assetPath = './ckanext/showcase/assets/';

module.exports = {
    // https://webpack.js.org/configuration/entry-context/
    entry: path.resolve(__dirname, assetPath, 'src/ckeditor.js'),

    // https://webpack.js.org/configuration/output/
    output: {
        path: path.resolve(__dirname, assetPath, 'build'),
        filename: 'ckeditor.js'
    },

    module: {
        rules: [
            {
                test: /ckeditor5-[^/\\]+[/\\]theme[/\\]icons[/\\][^/\\]+\.svg$/,

                use: [ 'raw-loader' ]
            },
            {
                test: /ckeditor5-[^/\\]+[/\\]theme[/\\].+\.css$/,

                use: [
                    {
                        loader: 'style-loader',
                        options: {
                            injectType: 'singletonStyleTag',
                            attributes: {
                                'data-cke': true
                            }
                        }
                    },
                    'css-loader',
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: styles.getPostCssConfig( {
                                themeImporter: {
                                    themePath: require.resolve( '@ckeditor/ckeditor5-theme-lark' )
                                },
                                minify: true
                            } )
                        }
                    }
                ]
            }
        ]
    },

    // By default webpack logs warnings if the bundle is bigger than 200kb.
    performance: { hints: false }
};
