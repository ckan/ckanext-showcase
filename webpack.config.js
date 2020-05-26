const CKEditorWebpackPlugin = require( '@ckeditor/ckeditor5-dev-webpack-plugin' );
const { styles } = require( '@ckeditor/ckeditor5-dev-utils' );
const path = require('path');
const assetPath = './ckanext/showcase/fanstatic/';

module.exports = {
    mode: 'production',
    entry: {
        "index": path.resolve(__dirname, assetPath, 'src/ckeditor.js'),
      },
    plugins: [
        new CKEditorWebpackPlugin({language: 'en'})
    ],
    output: {
        path: path.resolve(__dirname, assetPath, 'dist'),
        filename: 'ckeditor.js',
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
                    {
                        loader: 'postcss-loader',
                        options: styles.getPostCssConfig( {
                            themeImporter: {
                                themePath: require.resolve( '@ckeditor/ckeditor5-theme-lark' )
                            },
                            minify: true
                        } )
                    },
                ]
            }
        ]
    }
};