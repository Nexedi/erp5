<?php
class oneclickconnect extends Module
{
  public function __construct()
  {
    $this->name = 'oneclickconnect';
    $this->tab = 'Products';
    $this->version = '';

    parent::__construct();

    $this->displayName = $this->l('One Click Connect');
    $this->description = $this->l('Synchronize all your data with the TioSafe platform.');
    $this->confirmUninstall = $this->l('Are you sure you want to uninstall the module One Click Connect?');
  }

  public function install()
  {
    if(!parent::install()
      || !$this->registerHook('leftColumn')
      || !Configuration::updateValue('MOD_EXPORT_ONECLICKCONNECT_URL', 'https://www.tiolive.com/en/tiolive_image/logo.png')
      || !$this->installModuleTab('AdminOneClickConnect', array(1=>'One Click Connect', 2=>'One Click Connect'), 2)
      || !$this->installModuleTab('AdminOneClickConnect', array(1=>'One Click Connect', 2=>'One Click Connect'), 3)
      || !$this->installModuleTab('AdminOneClickConnect', array(1=>'One Click Connect', 2=>'One Click Connect'), 1))
      return false;
    return true;
  }

  private function installModuleTab($tabClass, $tabName, $idTabParent)
  {
    @copy(_PS_MODULE_DIR_.$this->name.'/logo.gif', _PS_IMG_DIR_.'t/'.$tabClass.'.gif');
    $tab = new Tab();
    $tab->name = $tabName;
    $tab->class_name = $tabClass;
    $tab->module = $this->name;
    $tab->id_parent = $idTabParent;
    if(!$tab->save())
      return false;
    return true;
  }

  public function uninstall()
  {
    if(!parent::uninstall()
      || !Configuration::deleteByName('MOD_EXPORT_ONECLICKCONNECT_URL')
      || !$this->uninstallModuleTab('AdminOneClickConnect'))
      return false;
    return true;
  }

  private function uninstallModuleTab($tabClass)
  {
    $idTab = Tab::getIdFromClassName($tabClass);
    if($idTab != 0)
    {
      $tab = new Tab($idTab);
      $tab->delete();
      return true;
    }
    return false;
  }

  public function getContent()
  {
    $html = '';
    $html .= '<h2>'.$this->l('One Click Connect: synchronize your data').'</h2>
    <fieldset>
<legend>'.$this->l('Informations  :').'</legend>'.$this->l("TioSafe allows you to synchronize your between multiple applications.").'<br />
	<br />'.$this->l('blablabla.').'
	<br />'.$this->l('bla.').'
	<br clear="all" />
	<br clear="all" />
	<a href="http://www.tiolive.com" target="_blank"><img src="https://www.tiolive.com/en/tiolive_image/logo.png" alt="Solution TioSafe" border="0" /></a>

    </fieldset>
<br clear="all" />
';
    return $html;
  }

	public function secureDir($dir)
	{
		define('_ONECLICKCONNECT_DIR_','/oneclickconnect');
		define('MSG_ALERT_MODULE_NAME',$this->l('Module One Click Connect should not be renamed'));
		
		if($dir != _ONECLICKCONNECT_DIR_)
		{
		    echo utf8_decode(MSG_ALERT_MODULE_NAME);	
			exit();
		}
	}

	public function netoyage_html($CatList)
	{
	  $CatList = strip_tags ($CatList);
	  $CatList = trim ($CatList);
	  $CatList = str_replace("&nbsp;"," ",$CatList);
	  $CatList = str_replace("&#39;","' ",$CatList);
	  $CatList = str_replace("&#150;","-",$CatList);
	  $CatList = str_replace(chr(9)," ",$CatList);
	  $CatList = str_replace(chr(10)," ",$CatList);
	  $CatList = str_replace(chr(13)," ",$CatList);
	  return $CatList;
	}
}
?>
