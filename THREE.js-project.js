      var geometry = new THREE.BoxGeometry( 3, 3, 3 );
      var material = new THREE.MeshBasicMaterial( { color: "#A49FEF", wireframe: true, transparent: true } );
      var cube01_wirefrane = new THREE.Mesh( geometry, material );
      scene.add( cube01_wireframe );
      
      var geometry = new THREE.BoxGeometry( 1, 1, 1 );
      var material = new THREE.MeshBasicMaterial( { color: "#433FEF" } );
      var cube02 = new THREE.Mesh( geometry, material );
      scene.add( cube02 );
      
      var geometry = new THREE.BoxGeometry( 3, 3, 3 );
      var material = new THREE.MeshBasicMaterial( { color: "#A49FEF", wireframe: true, transparent: true } );
      var cube02_wireframe = new THREE.Mesh( geometry, material );
      scene.add( cube02_wireframe );
      
      var geometry = new THREE.BoxGeometry( 10, 0.05, 0.5 );
      var material = new THREE.MeshBasicMaterial( { color: "#00FFBC" } );
      var bar01 = new THREE.Mesh( geometry, material );
      
      var geometry = new THREE.BoxGeometry( 10, 0.05, 0.5 );
      var material = new THREE.MeshBasicMaterial( { color: "#FFFFFF" } );
      var bar02 = new THREE.Mesh( geometry, material );
      
      var render = function() {
        requestAnimationFrame( render );
        
        cube01.rotation.x += 0.01;
        cube01.rotation.y += 0.01;
        
        cube01_wireframe.rotation.x += 0.01;
        cube01_wireframe.rotation.y += 0.01;
  
        cube02.rotation.x -= 0.01;
        cube02.rotation.y -= 0.01;
        
        cube02_wireframe.rotation.x -= 0.01;
        cube02_wireframe.rotation.y -= 0.01;

        bar01.rotation.z -= 0.01;
        bar02.rotation.z += 0.01;
        
        renderer.render( scene, camera );
      };
      
      render();
